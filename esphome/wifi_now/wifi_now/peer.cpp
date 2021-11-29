#include "peer.h"

namespace esphome {
namespace wifi_now {

static const char *TAG = "wifi_now.peer";

WifiNowPeer::WifiNowPeer() {}

void WifiNowPeer::set_bssid(bssid_t bssid) { this->bssid_ = bssid; }

const bssid_t &WifiNowPeer::get_bssid() const { return this->bssid_; }

void WifiNowPeer::set_aeskey(aeskey_t aeskey) { this->aeskey_ = aeskey; }

void WifiNowPeer::set_aeskey(optional<aeskey_t> aeskey) { this->aeskey_ = aeskey; }

const optional<aeskey_t> &WifiNowPeer::get_aeskey() const { return this->aeskey_; }

}  // namespace wifi_now
}  // namespace esphome
