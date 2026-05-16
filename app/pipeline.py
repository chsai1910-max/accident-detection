# # import gi
# # gi.require_version("Gst", "1.0")

# # from gi.repository import Gst, GLib

# # import pyds
# # import json

# # from loguru import logger

# # from app.class_map import CLASS_MAP
# # from app.tracker_state import TrackerStateManager
# # from app.event_detector import EventDetector

# # Gst.init(None)


# # class DeepStreamTrafficPipeline:

# #     def __init__(
# #         self,
# #         input_path,
# #         output_path,
# #         events_path,
# #         pgie_config,
# #         analytics_config
# #     ):

# #         self.input_path = input_path
# #         self.output_path = output_path
# #         self.events_path = events_path

# #         self.pgie_config = pgie_config
# #         self.analytics_config = analytics_config

# #         self.pipeline = None

# #         self.tracker_state = TrackerStateManager()
# #         self.event_detector = EventDetector()

# #         self.events = []

# #     def build(self):

# #         logger.info("Building DeepStream pipeline")

# #         pipeline_str = f"""

# #             filesrc location={self.input_path} !

# #             qtdemux !

# #             queue !

# #             h264parse !

# #             queue !

# #             nvv4l2decoder !

# #             queue !

# #             nvvideoconvert !

# #             video/x-raw(memory:NVMM), format=NV12 !

# #             mux.sink_0

# #             nvstreammux name=mux
# #                 batch-size=1
# #                 width=1920
# #                 height=1080
# #                 live-source=0
# #                 batched-push-timeout=40000 !

# #             queue !

# #             nvinfer
# #                 config-file-path={self.pgie_config} !

# #             queue !

# #             nvtracker
# #                 tracker-width=640
# #                 tracker-height=384
# #                 gpu-id=0
# #                 ll-lib-file=/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so
# #                 ll-config-file=/opt/nvidia/deepstream/deepstream/samples/configs/deepstream-app/config_tracker_NvDCF_perf.yml !

# #             queue !

# #             nvdsanalytics
# #                 config-file={self.analytics_config} !

# #             queue !

# #             nvdsosd !

# #             queue !

# #             nvvideoconvert !

# #             video/x-raw(memory:NVMM), format=NV12 !

# #             queue !

# #             nvv4l2h264enc bitrate=4000000 !

# #             h264parse !

# #             qtmux !

# #             filesink
# #                 location={self.output_path}
# #                 sync=false
# #                 async=false
# #         """

# #         logger.info(pipeline_str)

# #         self.pipeline = Gst.parse_launch(
# #             pipeline_str
# #         )

# #         if not self.pipeline:
# #             raise RuntimeError(
# #                 "Failed to create pipeline"
# #             )

# #         osd = self.pipeline.get_by_name(
# #             "nvdsosd0"
# #         )

# #         if osd:

# #             pad = osd.get_static_pad(
# #                 "sink"
# #             )

# #             if pad:

# #                 pad.add_probe(
# #                     Gst.PadProbeType.BUFFER,
# #                     self.osd_sink_pad_buffer_probe,
# #                     0
# #                 )

# #     def osd_sink_pad_buffer_probe(
# #         self,
# #         pad,
# #         info,
# #         u_data
# #     ):

# #         gst_buffer = info.get_buffer()

# #         if not gst_buffer:
# #             return Gst.PadProbeReturn.OK

# #         batch_meta = (
# #             pyds.gst_buffer_get_nvds_batch_meta(
# #                 hash(gst_buffer)
# #             )
# #         )

# #         if not batch_meta:
# #             return Gst.PadProbeReturn.OK

# #         l_frame = batch_meta.frame_meta_list

# #         while l_frame:

# #             try:

# #                 frame_meta = (
# #                     pyds.NvDsFrameMeta.cast(
# #                         l_frame.data
# #                     )
# #                 )

# #             except StopIteration:
# #                 break

# #             frame_num = frame_meta.frame_num

# #             detected_objects = []

# #             l_obj = frame_meta.obj_meta_list

# #             while l_obj:

# #                 try:

# #                     obj_meta = (
# #                         pyds.NvDsObjectMeta.cast(
# #                             l_obj.data
# #                         )
# #                     )

# #                 except StopIteration:
# #                     break

# #                 class_id = obj_meta.class_id

# #                 bbox = [

# #                     int(obj_meta.rect_params.left),

# #                     int(obj_meta.rect_params.top),

# #                     int(
# #                         obj_meta.rect_params.left +
# #                         obj_meta.rect_params.width
# #                     ),

# #                     int(
# #                         obj_meta.rect_params.top +
# #                         obj_meta.rect_params.height
# #                     )
# #                 ]

# #                 tracking = (
# #                     self.tracker_state.update_object(
# #                         int(obj_meta.object_id),
# #                         bbox
# #                     )
# #                 )

# #                 detected_objects.append({

# #                     "id": int(
# #                         obj_meta.object_id
# #                     ),

# #                     "class": CLASS_MAP.get(
# #                         class_id,
# #                         "Unknown"
# #                     ),

# #                     "bbox": bbox,

# #                     "position": tracking[
# #                         "position"
# #                     ],

# #                     "trajectory": tracking[
# #                         "trajectory"
# #                     ],

# #                     "speed": tracking[
# #                         "speed"
# #                     ]
# #                 })

# #                 try:
# #                     l_obj = l_obj.next

# #                 except StopIteration:
# #                     break

# #             events = (
# #                 self.event_detector.evaluate(
# #                     frame_num,
# #                     detected_objects
# #                 )
# #             )

# #             self.events.extend(events)

# #             try:
# #                 l_frame = l_frame.next

# #             except StopIteration:
# #                 break

# #         return Gst.PadProbeReturn.OK

# #     def run(self):

# #         logger.info("Starting pipeline")

# #         ret = self.pipeline.set_state(
# #             Gst.State.PLAYING
# #         )

# #         if ret == Gst.StateChangeReturn.FAILURE:

# #             logger.error(
# #                 "Failed to start pipeline"
# #             )

# #             return

# #         bus = self.pipeline.get_bus()

# #         bus.add_signal_watch()

# #         loop = GLib.MainLoop()

# #         def bus_call(
# #             bus,
# #             message,
# #             loop
# #         ):

# #             t = message.type

# #             if t == Gst.MessageType.EOS:

# #                 logger.success(
# #                     "End of stream"
# #                 )

# #                 loop.quit()

# #             elif t == Gst.MessageType.ERROR:

# #                 err, debug = (
# #                     message.parse_error()
# #                 )

# #                 logger.error(err)

# #                 logger.error(debug)

# #                 loop.quit()

# #             return True

# #         bus.connect(
# #             "message",
# #             bus_call,
# #             loop
# #         )

# #         try:

# #             loop.run()

# #         except KeyboardInterrupt:

# #             logger.warning(
# #                 "Interrupted by user"
# #             )

# #         finally:

# #             logger.info(
# #                 "Stopping pipeline"
# #             )

# #             self.pipeline.send_event(
# #                 Gst.Event.new_eos()
# #             )

# #             self.pipeline.set_state(
# #                 Gst.State.NULL
# #             )

# #             with open(
# #                 self.events_path,
# #                 "w"
# #             ) as f:

# #                 json.dump(
# #                     self.events,
# #                     f,
# #                     indent=2
# #                 )

# #             logger.success(
# #                 f"Events saved to {self.events_path}"
# #             )

# #             logger.success(
# #                 f"Output saved to {self.output_path}"
# #             )




# import gi
# gi.require_version("Gst", "1.0")

# from gi.repository import Gst, GLib

# import pyds
# import json

# from loguru import logger

# from app.class_map import CLASS_MAP
# from app.tracker_state import TrackerStateManager
# from app.event_detector import EventDetector

# Gst.init(None)


# class DeepStreamTrafficPipeline:

#     def __init__(
#         self,
#         input_path,
#         output_path,
#         events_path,
#         pgie_config,
#         analytics_config
#     ):

#         self.input_path = input_path
#         self.output_path = output_path
#         self.events_path = events_path

#         self.pgie_config = pgie_config
#         self.analytics_config = analytics_config

#         self.pipeline = None

#         self.tracker_state = TrackerStateManager()
#         self.event_detector = EventDetector()

#         self.events = []

#     def build(self):

#         logger.info("Building DeepStream pipeline")

#         pipeline_str = f"""

#             filesrc location={self.input_path} !

#             qtdemux !

#             queue !

#             h264parse !

#             queue !

#             nvv4l2decoder !

#             queue !

#             nvvideoconvert !

#             video/x-raw(memory:NVMM), format=NV12 !

#             mux.sink_0

#             nvstreammux name=mux
#                 batch-size=1
#                 width=1920
#                 height=1080
#                 live-source=0
#                 batched-push-timeout=40000 !

#             queue !

#             nvinfer
#                 config-file-path={self.pgie_config} !

#             queue !

#             nvtracker
#                 tracker-width=640
#                 tracker-height=384
#                 gpu-id=0
#                 ll-lib-file=/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so
#                 ll-config-file=/opt/nvidia/deepstream/deepstream/samples/configs/deepstream-app/config_tracker_NvDCF_perf.yml !

#             queue !

#             nvdsanalytics
#                 config-file={self.analytics_config} !

#             queue !

#             nvdsosd !

#             queue !

#             nvvideoconvert !

#             video/x-raw(memory:NVMM), format=NV12 !

#             queue !

#             nvv4l2h264enc bitrate=4000000 !

#             h264parse !

#             # matroskamux !
#             avimux !

#             filesink
#                 location={self.output_path}
#                 sync=false
#                 async=false
#         """

#         logger.info(pipeline_str)

#         self.pipeline = Gst.parse_launch(
#             pipeline_str
#         )

#         if not self.pipeline:
#             raise RuntimeError(
#                 "Failed to create pipeline"
#             )

#         osd = self.pipeline.get_by_name(
#             "nvdsosd0"
#         )

#         if osd:

#             pad = osd.get_static_pad(
#                 "sink"
#             )

#             if pad:

#                 pad.add_probe(
#                     Gst.PadProbeType.BUFFER,
#                     self.osd_sink_pad_buffer_probe,
#                     0
#                 )

#     def osd_sink_pad_buffer_probe(
#         self,
#         pad,
#         info,
#         u_data
#     ):

#         gst_buffer = info.get_buffer()

#         if not gst_buffer:
#             return Gst.PadProbeReturn.OK

#         batch_meta = (
#             pyds.gst_buffer_get_nvds_batch_meta(
#                 hash(gst_buffer)
#             )
#         )

#         if not batch_meta:
#             return Gst.PadProbeReturn.OK

#         l_frame = batch_meta.frame_meta_list

#         while l_frame:

#             try:

#                 frame_meta = (
#                     pyds.NvDsFrameMeta.cast(
#                         l_frame.data
#                     )
#                 )

#             except StopIteration:
#                 break

#             frame_num = frame_meta.frame_num

#             detected_objects = []

#             l_obj = frame_meta.obj_meta_list

#             while l_obj:

#                 try:

#                     obj_meta = (
#                         pyds.NvDsObjectMeta.cast(
#                             l_obj.data
#                         )
#                     )

#                 except StopIteration:
#                     break

#                 class_id = obj_meta.class_id

#                 bbox = [

#                     int(obj_meta.rect_params.left),

#                     int(obj_meta.rect_params.top),

#                     int(
#                         obj_meta.rect_params.left +
#                         obj_meta.rect_params.width
#                     ),

#                     int(
#                         obj_meta.rect_params.top +
#                         obj_meta.rect_params.height
#                     )
#                 ]

#                 tracking = (
#                     self.tracker_state.update_object(
#                         int(obj_meta.object_id),
#                         bbox
#                     )
#                 )

#                 detected_objects.append({

#                     "id": int(
#                         obj_meta.object_id
#                     ),

#                     "class": CLASS_MAP.get(
#                         class_id,
#                         "Unknown"
#                     ),

#                     "bbox": bbox,

#                     "position": tracking[
#                         "position"
#                     ],

#                     "trajectory": tracking[
#                         "trajectory"
#                     ],

#                     "speed": tracking[
#                         "speed"
#                     ]
#                 })

#                 try:
#                     l_obj = l_obj.next

#                 except StopIteration:
#                     break

#             events = (
#                 self.event_detector.evaluate(
#                     frame_num,
#                     detected_objects
#                 )
#             )

#             self.events.extend(events)

#             try:
#                 l_frame = l_frame.next

#             except StopIteration:
#                 break

#         return Gst.PadProbeReturn.OK

#     def run(self):

#         logger.info("Starting pipeline")

#         ret = self.pipeline.set_state(
#             Gst.State.PLAYING
#         )

#         if ret == Gst.StateChangeReturn.FAILURE:

#             logger.error(
#                 "Failed to start pipeline"
#             )

#             return

#         bus = self.pipeline.get_bus()

#         bus.add_signal_watch()

#         loop = GLib.MainLoop()

#         def bus_call(
#             bus,
#             message,
#             loop
#         ):

#             t = message.type

#             if t == Gst.MessageType.EOS:

#                 logger.success(
#                     "End of stream"
#                 )

#                 loop.quit()

#             elif t == Gst.MessageType.ERROR:

#                 err, debug = (
#                     message.parse_error()
#                 )

#                 logger.error(err)

#                 logger.error(debug)

#                 loop.quit()

#             return True

#         bus.connect(
#             "message",
#             bus_call,
#             loop
#         )

#         try:

#             loop.run()

#         except KeyboardInterrupt:

#             logger.warning(
#                 "Interrupted by user"
#             )

#         finally:

#             logger.info(
#                 "Stopping pipeline"
#             )

#             self.pipeline.send_event(
#                 Gst.Event.new_eos()
#             )

#             self.pipeline.set_state(
#                 Gst.State.NULL
#             )

#             with open(
#                 self.events_path,
#                 "w"
#             ) as f:

#                 json.dump(
#                     self.events,
#                     f,
#                     indent=2
#                 )

#             logger.success(
#                 f"Events saved to {self.events_path}"
#             )

#             logger.success(
#                 f"Output saved to {self.output_path}"
#             )




import gi
gi.require_version("Gst", "1.0")

from gi.repository import Gst, GLib

import pyds
import json

from loguru import logger

from app.class_map import CLASS_MAP
from app.tracker_state import TrackerStateManager
from app.event_detector import EventDetector

Gst.init(None)


class DeepStreamTrafficPipeline:

    def __init__(
        self,
        input_path,
        output_path,
        events_path,
        pgie_config,
        analytics_config
    ):

        self.input_path = input_path
        self.output_path = output_path
        self.events_path = events_path

        self.pgie_config = pgie_config
        self.analytics_config = analytics_config

        self.pipeline = None

        self.tracker_state = TrackerStateManager()
        self.event_detector = EventDetector()

        self.events = []

    def build(self):

        logger.info("Building DeepStream pipeline")

        pipeline_str = f"""

            filesrc location={self.input_path} !

            qtdemux !

            queue !

            h264parse !

            queue !

            nvv4l2decoder !

            queue !

            nvvideoconvert !

            video/x-raw(memory:NVMM), format=NV12 !

            mux.sink_0

            nvstreammux name=mux
                batch-size=1
                width=1920
                height=1080
                live-source=0
                batched-push-timeout=40000 !

            queue !

            nvinfer
                config-file-path={self.pgie_config} !

            queue !

            nvtracker
                tracker-width=640
                tracker-height=384
                gpu-id=0
                ll-lib-file=/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so
                ll-config-file=/opt/nvidia/deepstream/deepstream/samples/configs/deepstream-app/config_tracker_NvDCF_perf.yml !

            queue !

            nvdsanalytics
                config-file={self.analytics_config} !

            queue !

            nvdsosd !

            queue !

            nvvideoconvert !

            queue !

            videoconvert !

            queue !

            x264enc
                bitrate=4000
                speed-preset=ultrafast
                tune=zerolatency !

            mp4mux faststart=true !

            filesink
                location={self.output_path}
                sync=false
                async=false
        """

        logger.info(pipeline_str)

        self.pipeline = Gst.parse_launch(
            pipeline_str
        )

        if not self.pipeline:
            raise RuntimeError(
                "Failed to create pipeline"
            )

        osd = self.pipeline.get_by_name(
            "nvdsosd0"
        )

        if osd:

            pad = osd.get_static_pad(
                "sink"
            )

            if pad:

                pad.add_probe(
                    Gst.PadProbeType.BUFFER,
                    self.osd_sink_pad_buffer_probe,
                    0
                )

    def osd_sink_pad_buffer_probe(
        self,
        pad,
        info,
        u_data
    ):

        gst_buffer = info.get_buffer()

        if not gst_buffer:
            return Gst.PadProbeReturn.OK

        batch_meta = (
            pyds.gst_buffer_get_nvds_batch_meta(
                hash(gst_buffer)
            )
        )

        if not batch_meta:
            return Gst.PadProbeReturn.OK

        l_frame = batch_meta.frame_meta_list

        while l_frame:

            try:

                frame_meta = (
                    pyds.NvDsFrameMeta.cast(
                        l_frame.data
                    )
                )

            except StopIteration:
                break

            frame_num = frame_meta.frame_num

            detected_objects = []

            l_obj = frame_meta.obj_meta_list

            while l_obj:

                try:

                    obj_meta = (
                        pyds.NvDsObjectMeta.cast(
                            l_obj.data
                        )
                    )

                except StopIteration:
                    break

                class_id = obj_meta.class_id

                bbox = [

                    int(obj_meta.rect_params.left),

                    int(obj_meta.rect_params.top),

                    int(
                        obj_meta.rect_params.left +
                        obj_meta.rect_params.width
                    ),

                    int(
                        obj_meta.rect_params.top +
                        obj_meta.rect_params.height
                    )
                ]

                tracking = (
                    self.tracker_state.update_object(
                        int(obj_meta.object_id),
                        bbox
                    )
                )

                detected_objects.append({

                    "id": int(
                        obj_meta.object_id
                    ),

                    "class": CLASS_MAP.get(
                        class_id,
                        "Unknown"
                    ),

                    "bbox": bbox,

                    "position": tracking[
                        "position"
                    ],

                    "trajectory": tracking[
                        "trajectory"
                    ],

                    "speed": tracking[
                        "speed"
                    ]
                })

                try:
                    l_obj = l_obj.next

                except StopIteration:
                    break

            events = (
                self.event_detector.evaluate(
                    frame_num,
                    detected_objects
                )
            )

            self.events.extend(events)

            try:
                l_frame = l_frame.next

            except StopIteration:
                break

        return Gst.PadProbeReturn.OK

    def run(self):

        logger.info("Starting pipeline")

        ret = self.pipeline.set_state(
            Gst.State.PLAYING
        )

        if ret == Gst.StateChangeReturn.FAILURE:

            logger.error(
                "Failed to start pipeline"
            )

            return

        bus = self.pipeline.get_bus()

        bus.add_signal_watch()

        loop = GLib.MainLoop()

        def bus_call(
            bus,
            message,
            loop
        ):

            t = message.type

            if t == Gst.MessageType.EOS:

                logger.success(
                    "End of stream"
                )

                loop.quit()

            elif t == Gst.MessageType.ERROR:

                err, debug = (
                    message.parse_error()
                )

                logger.error(err)

                logger.error(debug)

                loop.quit()

            return True

        bus.connect(
            "message",
            bus_call,
            loop
        )

        try:

            loop.run()

        except KeyboardInterrupt:

            logger.warning(
                "Interrupted by user"
            )

        finally:

            logger.info(
                "Stopping pipeline"
            )

            self.pipeline.send_event(
                Gst.Event.new_eos()
            )

            self.pipeline.set_state(
                Gst.State.NULL
            )

            with open(
                self.events_path,
                "w"
            ) as f:

                json.dump(
                    self.events,
                    f,
                    indent=2
                )

            logger.success(
                f"Events saved to {self.events_path}"
            )

            logger.success(
                f"Output saved to {self.output_path}"
            )