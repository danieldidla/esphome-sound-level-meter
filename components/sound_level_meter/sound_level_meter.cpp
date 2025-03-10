#include "sound_level_meter.h"

namespace esphome {
namespace sound_level_meter {

static const char *const TAG = "sound_level_meter";
static constexpr float DBFS_OFFSET = 20 * log10(sqrt(2));

void SoundLevelMeter::set_update_interval(uint32_t update_interval) { this->update_interval_ = update_interval; }
uint32_t SoundLevelMeter::get_update_interval() { return this->update_interval_; }
void SoundLevelMeter::set_buffer_size(uint32_t buffer_size) { this->buffer_size_ = buffer_size; }
uint32_t SoundLevelMeter::get_buffer_size() { return this->buffer_size_; }
uint32_t SoundLevelMeter::get_sample_rate() { return this->i2s_->get_sample_rate(); }
void SoundLevelMeter::set_i2s(i2s::I2SComponent *i2s) { this->i2s_ = i2s; }
void SoundLevelMeter::add_group(SensorGroup *group) { this->groups_.push_back(group); }
void SoundLevelMeter::set_warmup_interval(uint32_t warmup_interval) { this->warmup_interval_ = warmup_interval; }

void SoundLevelMeter::dump_config() {
  ESP_LOGCONFIG(TAG, "Sound Level Meter:");
  ESP_LOGCONFIG(TAG, "  Buffer Size: %u (samples)", this->buffer_size_);
  ESP_LOGCONFIG(TAG, "  Sample Rate: %u Hz", this->get_sample_rate());
  LOG_UPDATE_INTERVAL(this);
}

void SoundLevelMeter::setup() {
  xTaskCreatePinnedToCore(SoundLevelMeter::task, "sound_level_meter", 4096, this, 1, nullptr, 1);
}

void SoundLevelMeter::task(void *param) {
  SoundLevelMeter *this_ = reinterpret_cast<SoundLevelMeter *>(param);
  std::vector<int16_t> buffer(this_->buffer_size_);

  while (1) {
    if (this_->i2s_->read_samples(buffer)) {
      std::vector<float> float_buffer(buffer.size());
      for (size_t i = 0; i < buffer.size(); i++) {
        float_buffer[i] = static_cast<float>(buffer[i]) / INT16_MAX;
      }

      for (auto *g : this_->groups_)
        g->process(float_buffer);
    }
  }
}

void SensorGroup::process(std::vector<float> &buffer) {
  float sum = 0;
  for (float sample : buffer) {
    sum += sample * sample;
  }
  float rms = sqrt(sum / buffer.size());
  float dB = 20 * log10(rms) + DBFS_OFFSET;
  for (auto s : this->sensors_)
    s->defer_publish_state(dB);
}

} // namespace sound_level_meter
} // namespace esphome
