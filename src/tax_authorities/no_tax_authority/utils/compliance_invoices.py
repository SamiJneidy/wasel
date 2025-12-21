from datetime import datetime, timezone
import pytz
KSA_TZ = pytz.timezone("Asia/Riyadh")
print(datetime.now(KSA_TZ).time().isoformat(timespec='seconds'))