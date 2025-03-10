# pylint: disable=no-name-in-module,invalid-name,unused-argument

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.automation import maybe_simple_id
from esphome.components import sensor, i2s_audio
from esphome.const import (
    CONF_ID,
    CONF_SENSORS,
    CONF_FILTERS,
    CONF_WINDOW_SIZE,
    CONF_UPDATE_INTERVAL,
    UNIT_DECIBEL,
    STATE_CLASS_MEASUREMENT
)

CODEOWNERS = ["@stas-sl"]
DEPENDENCIES = ["esp32", "i2s_audio"]
AUTO_LOAD = ["sensor"]
MULTI_CONF = True

pcm1808_ns = cg.esphome_ns.namespace("pcm1808")
PCM1808Component = pcm1808_ns.class_("PCM1808Component", cg.Component)
PCM1808Sensor = pcm1808_ns.class_("PCM1808Sensor", sensor.Sensor)

CONF_I2S_AUDIO_ID = "i2s_audio_id"
CONF_BUFFER_SIZE = "buffer_size"
CONF_TASK_STACK_SIZE = "task_stack_size"
CONF_TASK_PRIORITY = "task_priority"
CONF_TASK_CORE = "task_core"
CONF_MIC_SENSITIVITY = "mic_sensitivity"
CONF_OFFSET = "offset"

ICON_WAVEFORM = "mdi:waveform"

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(PCM1808Component),
            cv.GenerateID(CONF_I2S_AUDIO_ID): cv.use_id(i2s_audio.I2SAudioComponent),
            cv.Optional(CONF_UPDATE_INTERVAL, default="60s"): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_BUFFER_SIZE, default=1024): cv.positive_not_null_int,
            cv.Optional(CONF_TASK_STACK_SIZE, default=4096): cv.positive_not_null_int,
            cv.Optional(CONF_TASK_PRIORITY, default=2): cv.uint8_t,
            cv.Optional(CONF_TASK_CORE, default=1): cv.int_range(0, 1),
            cv.Optional(CONF_MIC_SENSITIVITY): cv.decibel,
            cv.Optional(CONF_OFFSET): cv.decibel,
            cv.Required(CONF_SENSORS): cv.ensure_list(sensor.sensor_schema(
                PCM1808Sensor,
                unit_of_measurement=UNIT_DECIBEL,
                accuracy_decimals=2,
                state_class=STATE_CLASS_MEASUREMENT,
                icon=ICON_WAVEFORM
            ))
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    i2s_audio_component = await cg.get_variable(config[CONF_I2S_AUDIO_ID])
    cg.add(var.set_i2s_audio(i2s_audio_component))
    cg.add(var.set_update_interval(config[CONF_UPDATE_INTERVAL]))
    cg.add(var.set_buffer_size(config[CONF_BUFFER_SIZE]))
    cg.add(var.set_task_stack_size(config[CONF_TASK_STACK_SIZE]))
    cg.add(var.set_task_priority(config[CONF_TASK_PRIORITY]))
    cg.add(var.set_task_core(config[CONF_TASK_CORE]))
    if CONF_MIC_SENSITIVITY in config:
        cg.add(var.set_mic_sensitivity(config[CONF_MIC_SENSITIVITY]))
    if CONF_OFFSET in config:
        cg.add(var.set_offset(config[CONF_OFFSET]))
    
    for sensor_config in config[CONF_SENSORS]:
        sens = await sensor.new_sensor(sensor_config)
        cg.add(var.add_sensor(sens))
