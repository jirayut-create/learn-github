class AccessPanelRtEvent:
    """ เก็บข้อมูลเหตุการณ์จากระบบควบคุมประตูแบบเรียลไทม์ """
    
    def __init__(self, time, pin, door, event_type, in_or_out, card=None):
        self.time = time
        self.pin = pin
        self.door = door
        self.event_type = event_type
        self.in_or_out = in_or_out
        self.card = card

    def get_door_id(self):
        """ แปลงค่า Door เป็น Integer """
        try:
            return int(self.door) if self.door and self.door != "0" else -1
        except ValueError:
            return -1

    def __str__(self):
        """ แปลงข้อมูลเหตุการณ์เป็นข้อความอ่านง่าย """
        description = self.get_description(self.event_type) or "Unknown event"
        
        if self.pin and self.pin != "0":
            user_status = "Entry" if self.in_or_out == 0 else "Exit" if self.in_or_out == 1 else "User"
            description += f", {user_status}: {self.pin}"
        
        if self.door and self.door != "0":
            description += f", Door: {self.door}"
        
        return f"* Event: {description}"

    @staticmethod
    def get_description(code):
        """ แปลงรหัสเหตุการณ์เป็นข้อความ """
        event_descriptions = {
            0: "Normal Punch Open",
            1: "Punch during Normal Open Time Zone",
            2: "First Card Normal Open",
            3: "Multi-Card Open",
            4: "Emergency Password Open",
            5: "Open during Normal Open Time Zone",
            6: "Linkage Event Triggered",
            7: "Alarm Canceled",
            8: "Remote Opening",
            9: "Remote Closing",
            10: "Disable Intraday Normal Open Time Zone",
            11: "Enable Intraday Normal Open Time Zone",
            12: "Open Auxiliary Output",
            13: "Close Auxiliary Output",
            14: "Press Fingerprint Open",
            15: "Multi-Card Open",
            16: "Press Fingerprint during Normal Open Time Zone",
            17: "Card plus Fingerprint Open",
            18: "First Card Normal Open",
            19: "First Card Normal Open",
            20: "Too Short Punch Interval",
            21: "Door Inactive Time Zone",
            22: "Illegal Time Zone",
            23: "Access Denied",
            24: "Anti-Passback",
            25: "Interlock",
            26: "Multi-Card Authentication",
            27: "Unregistered Card",
            28: "Opening Timeout",
            29: "Card Expired",
            30: "Password Error",
            31: "Too Short Fingerprint Pressing Interval",
            32: "Multi-Card Authentication",
            33: "Fingerprint Expired",
            34: "Unregistered Fingerprint",
            35: "Door Inactive Time Zone",
            36: "Failed to Close during Normal Open Time Zone",
            101: "Duress Password Open",
            102: "Opened Accidentally",
            103: "Duress Fingerprint Open",
            200: "Door Opened Correctly",
            204: "Normal Open Time Zone Over",
            205: "Remote Normal Opening",
            206: "Device Start",
            220: "Auxiliary Input Disconnected",
            221: "Auxiliary Input Shorted",
        }
        return event_descriptions.get(code, None)

# 📌 ตัวอย่างการใช้งาน
event1 = AccessPanelRtEvent("2025-03-04 19:22:54", "12345", "1", 200, 0)
event2 = AccessPanelRtEvent("2025-03-04 19:23:00", "67890", "2", 23, 1, card=555555)

print(event1)
print(event2)
