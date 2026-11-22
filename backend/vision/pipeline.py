# vision/pipeline.py - the main detection loop (runs in a background thread)
#
# camera -> resize -> YOLO + tracker -> count per shelf -> save to database
#                                    -> draw boxes -> JPEG for the live page

import threading
import time

from ..config import SAVE_INTERVAL
from ..database import SessionLocal
from ..models import Shelf, Product, Inventory
from ..services import inventory_service
from .tracking import TrackHistory
from .counting import count_by_shelf
from . import shelf_monitor


class DetectionPipeline:
    def __init__(self):
        self.thread = None
        self.stop_flag = threading.Event()
        self.latest_jpeg = None          # newest annotated frame
        self.status = self._empty_status()

    def _empty_status(self):
        return {"running": False, "state": "Stopped", "source": "", "fps": 0,
                "counts": {}, "message": ""}

    def is_running(self):
        return self.thread is not None and self.thread.is_alive()

    # ---------- start / stop ----------
    def start(self, source):
        if self.is_running():
            raise RuntimeError("Detection is already running")

        self.stop_flag.clear()
        self.latest_jpeg = None
        self.status = self._empty_status()
        self.status.update({"running": True, "state": "Starting", "source": source})

        self.thread = threading.Thread(target=self._run, args=(source,), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag.set()
        if self.thread is not None:
            self.thread.join(timeout=8)

    # ---------- load shelf regions from the database ----------
    def _load_shelves(self, db):
        shelves = []
        for shelf in db.query(Shelf).filter(Shelf.status == "Active").all():
            if shelf.roi_w > 0 and shelf.roi_h > 0:
                shelves.append({
                    "shelf_id": shelf.shelf_id, "name": shelf.shelf_name,
                    "roi_x": shelf.roi_x, "roi_y": shelf.roi_y,
                    "roi_w": shelf.roi_w, "roi_h": shelf.roi_h,
                    "occupancy": shelf.occupancy, "roi": None,
                })
        return shelves

    # ---------- save counts in the database ----------
    def _save(self, db, counts, shelf_rois, occupancy):
        # YOLO class name -> product
        product_by_class = {}
        for product in db.query(Product).all():
            if product.detect_class:
                product_by_class[product.detect_class.lower()] = product

        for item in shelf_rois:
            shelf = db.query(Shelf).filter(Shelf.shelf_id == item["shelf_id"]).first()
            if shelf is None:
                continue
            shelf_counts = counts.get(item["shelf_id"], {})

            # 1. products seen on this shelf
            for label, qty in shelf_counts.items():
                product = product_by_class.get(label)
                if product is not None:
                    inventory_service.update_stock(db, product, shelf, qty)

            # 2. products that were on this shelf before but are not seen now
            old_rows = db.query(Inventory).filter(Inventory.shelf_id == shelf.shelf_id).all()
            for row in old_rows:
                label = (row.product.detect_class or "").lower()
                if label and label not in shelf_counts and row.detected_quantity != 0:
                    inventory_service.update_stock(db, row.product, shelf, 0)

            # 3. how full the shelf is
            inventory_service.update_shelf_occupancy(db, shelf, occupancy.get(item["shelf_id"], 0))

    # ---------- main loop ----------
    def _run(self, source):
        db = SessionLocal()
        cap = None
        try:
            import cv2
            from .camera import open_source, resize_frame
            from .detection import load_model, detect_and_track

            self.status["state"] = "Loading model"
            load_model()
            cap = open_source(source)

            shelf_rois = self._load_shelves(db)
            if len(shelf_rois) == 0:
                self.status["message"] = "No shelf regions are set, so nothing is saved. Add a region on the Shelves page."

            history = TrackHistory(window=30)
            frame_number = 0
            fps_count = 0
            fps_time = time.time()
            last_save = time.time()
            self.status["state"] = "Running"

            while not self.stop_flag.is_set():
                ok, frame = cap.read()
                if not ok:
                    self.status["state"] = "Finished"
                    self.status["message"] = "Video ended"
                    break

                frame = resize_frame(frame)
                height, width = frame.shape[:2]
                frame_number += 1

                # shelf regions in pixels (same for every frame of this video)
                for item in shelf_rois:
                    item["roi"] = shelf_monitor.roi_to_pixels(item, width, height)

                detections = detect_and_track(frame)
                counts = count_by_shelf(detections, shelf_rois, history, frame_number)

                # how full is each shelf right now
                occupancy = {}
                for item in shelf_rois:
                    boxes = [d["box"] for d in detections
                             if shelf_monitor.center_inside(d["box"], item["roi"])]
                    occupancy[item["shelf_id"]] = shelf_monitor.occupancy_percent(item["roi"], boxes)
                    item["occupancy"] = occupancy[item["shelf_id"]]

                # save in the database every few seconds
                if time.time() - last_save >= SAVE_INTERVAL:
                    self._save(db, counts, shelf_rois, occupancy)
                    last_save = time.time()

                # totals for the live page
                totals = {}
                for det in detections:
                    totals[det["label"]] = totals.get(det["label"], 0) + 1
                self.status["counts"] = totals

                # draw and keep the JPEG
                frame = shelf_monitor.draw_overlay(frame, shelf_rois, detections)
                ok, jpeg = cv2.imencode(".jpg", frame)
                if ok:
                    self.latest_jpeg = jpeg.tobytes()

                # FPS
                fps_count += 1
                if time.time() - fps_time >= 1:
                    self.status["fps"] = fps_count
                    fps_count = 0
                    fps_time = time.time()

        except Exception as error:
            print("Detection error:", error)
            self.status["state"] = "Error"
            self.status["message"] = str(error)
        finally:
            if cap is not None:
                cap.release()
            db.close()
            self.status["running"] = False
            if self.status["state"] in ("Running", "Starting", "Loading model"):
                self.status["state"] = "Stopped"
            self.status["fps"] = 0


# one pipeline for the whole application
pipeline = DetectionPipeline()
