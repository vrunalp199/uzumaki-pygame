import os
import time as __time_for_esp
import threading
import subprocess
import webbrowser

try:
    import RPi.GPIO as GPIO
    HAVE_GPIO = True
except Exception:
    GPIO = None
    HAVE_GPIO = False


try:
    import webview
    WEBVIEW_AVAILABLE = True
except Exception:
    webview = None
    WEBVIEW_AVAILABLE = False

ESP_EN_PIN = 17


_embedded_window = None
_embedded_thread = None
deauth_status_text = "ESP OFF"

def esp_setup():
    """
    Initialize GPIO pin for ESP8266 power control.
    """
    if not HAVE_GPIO or GPIO is None:
        print("[ESP] GPIO not available on this platform.")
        return

    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ESP_EN_PIN, GPIO.OUT, initial=GPIO.LOW)

        print(f"[ESP] GPIO {ESP_EN_PIN} configured.")

    except Exception as e:
        print("[ESP] GPIO setup error:", e)

def esp_on():
    """
    Power ON ESP8266.
    """
    print("[*] Powering ESP8266 ON.")

    try:
        if HAVE_GPIO and GPIO is not None:
            GPIO.output(ESP_EN_PIN, GPIO.HIGH)

        __time_for_esp.sleep(4)

    except Exception as e:
        print("[ESP] Failed to power ON:", e)

def esp_off():
    """
    Power OFF ESP8266.
    """
    print("[*] Powering ESP8266 OFF.")

    try:
        if HAVE_GPIO and GPIO is not None:
            GPIO.output(ESP_EN_PIN, GPIO.LOW)

        __time_for_esp.sleep(0.5)

    except Exception as e:
        print("[ESP] Failed to power OFF:", e)

def connect_to_esp_wifi(
    ssid="pwned",
    password="deauther",
    interface="wlan1"
):
    """
    Connect Linux WiFi adapter to ESP8266 AP.
    """

    print(f"[ESP] Connecting to WiFi '{ssid}' using {interface}...")

    try:
        result = subprocess.run(
            [
                "nmcli",
                "device",
                "wifi",
                "connect",
                ssid,
                "password",
                password,
                "ifname",
                interface
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("[ESP] Connected successfully.")
        else:
            print("[ESP] Connection failed:")
            print(result.stderr)

    except FileNotFoundError:
        print("[ESP] nmcli not found. Install NetworkManager.")

    except Exception as e:
        print("[ESP] Connection error:", e)

    __time_for_esp.sleep(4)

def _open_embedded_browser(
    url="http://192.168.4.1",
    title="ESP Web UI"
):
    """
    Open ESP8266 web UI in pywebview.
    """

    global _embedded_window
    global _embedded_thread

    if not WEBVIEW_AVAILABLE:
        print("[ESP] pywebview not installed.")
        print("[ESP] Opening external browser instead.")
        webbrowser.open(url)
        return

    def _create():
        global _embedded_window

        try:
            _embedded_window = webview.create_window(
                title,
                url,
                width=1000,
                height=700,
                resizable=True
            )

            webview.start(debug=False)

        except Exception as e:
            print("[ESP] Webview error:", e)

    try:
        _embedded_thread = threading.Thread(
            target=_create,
            daemon=True
        )

        _embedded_thread.start()

        __time_for_esp.sleep(1)

    except Exception as e:
        print("[ESP] Failed to start embedded browser:", e)

def _close_embedded_browser():
    """
    Close pywebview window.
    """

    global _embedded_window

    try:
        if WEBVIEW_AVAILABLE and _embedded_window:

            try:
                _embedded_window.destroy()

            except Exception:
                try:
                    for w in webview.windows:
                        w.destroy()
                except Exception:
                    pass

            _embedded_window = None

            print("[ESP] Embedded browser closed.")

    except Exception as e:
        print("[ESP] Error closing browser:", e)

def deauther_power_on():
    """
    Setup GPIO and power ON ESP8266.
    """

    global deauth_status_text

    esp_setup()
    esp_on()

    deauth_status_text = "ESP Powered ON"

    print("[ESP] Status:", deauth_status_text)

def deauther_connect_and_open(
    embedded=True,
    ssid="pwned",
    password="deauther",
    interface="wlan1"
):
    """
    Connect to ESP WiFi and open web UI.
    """

    global deauth_status_text

    connect_to_esp_wifi(
        ssid=ssid,
        password=password,
        interface=interface
    )

    if embedded:
        _open_embedded_browser("http://192.168.4.1")
    else:
        webbrowser.open("http://192.168.4.1")

    deauth_status_text = "ESP Web UI Opened"

    print("[ESP] Status:", deauth_status_text)

def deauther_power_off_and_close():
    """
    Close browser and power OFF ESP8266.
    """

    global deauth_status_text

    _close_embedded_browser()

    esp_off()

    deauth_status_text = "ESP Powered OFF"

    print("[ESP] Status:", deauth_status_text)


def esp_cleanup():
    """
    Cleanup GPIO safely.
    """
    try:
        if HAVE_GPIO and GPIO is not None:
            GPIO.cleanup()

            print("[ESP] GPIO cleaned up.")

    except Exception as e:
        print("[ESP] Cleanup error:", e)


if __name__ == "__main__":

    deauther_power_on()

    deauther_connect_and_open(
        embedded=True,
        interface="wlan1"
    )

    input("Press ENTER to shutdown ESP...")

    deauther_power_off_and_close()

    esp_cleanup()