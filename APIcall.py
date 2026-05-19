from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from sk import my_sk
import time
import json

app = Flask(__name__)

client = OpenAI(
    api_key=my_sk,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

OFFLINE_DB = {
    "flashing folder": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: Your Mac is turning on, but it cannot find its hard drive or operating system.\n"
            "What it means: The internal storage is either disconnected, broken, or completely erased.\n"
            "What to do: Try starting up in 'Recovery Mode' by holding Command+R while turning it on to reinstall macOS. If the drive still doesn't show up, a loose cable may need reseating — this is a relatively affordable fix at an Authorized Apple Service Provider or independent repair shop."
        ),
        "score": 4
    },
    "circle with slash": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: You see a circle with a line through it when turning on the computer.\n"
            "What it means: Your Mac found an operating system, but it is the wrong version or the files are corrupted. This is a software issue, not a hardware failure.\n"
            "What to do: Try restarting in 'Safe Mode' by holding the Shift key. If that fails, hold Command+R to enter Recovery Mode and reinstall macOS without losing your files. No repair shop visit is needed — this is a simple fix you can do at home."
        ),
        "score": 2
    },
    "padlock icon": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: A padlock screen is asking for a password right when the computer turns on, before macOS even loads.\n"
            "What it means: The computer has a firmware password set to prevent unauthorized use, or it was locked by an IT department or a previous owner.\n"
            "What to do: You must enter the firmware password. If you have forgotten it, take the Mac along with your original proof of purchase to an Apple Store — they can remove it for free. Do not recycle this device, as the hardware itself is perfectly fine."
        ),
        "score": 5
    },
    "kernel panic": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: The screen says 'Your computer restarted because of a problem' in multiple languages.\n"
            "What it means: The computer experienced a major crash called a 'kernel panic,' usually caused by failing hardware or a bad software update.\n"
            "What to do: First, make sure your macOS is fully updated and unplug all extra devices (printers, hard drives, etc.). If it keeps happening, you may have a failing battery or broken graphics chip. Take it to an Authorized Apple Service Provider for diagnosis — repair costs vary, so ask for a quote before committing."
        ),
        "score": 6
    },
    "target disk mode": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: The screen just shows a floating lightning bolt or Firewire logo and nothing else.\n"
            "What it means: Your Mac is stuck in 'Target Disk Mode,' which means it thinks it is plugged in as an external hard drive for another computer.\n"
            "What to do: Check if the 'T' key on your keyboard is physically stuck down — simply unsticking it will fix the problem immediately. If the key is not stuck, there may be minor liquid damage on the keyboard causing it to register automatically. A keyboard cleaning or replacement is a straightforward repair at most shops."
        ),
        "score": 3
    },

    # ==========================================
    # MACOS LOGIC BOARD & BEEP CODES
    # ==========================================
    "1 beep": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: Your computer is beeping once every 5 seconds and will not turn on.\n"
            "What it means: The computer cannot detect its internal memory (RAM). Without memory, the Mac cannot start at all.\n"
            "What to do: On older Macs with removable RAM, the memory sticks may just need to be taken out and clicked back in. On newer models, the memory is soldered to the board and requires professional micro-soldering repair. Take it to an Authorized Apple Service Provider for a quote — if the repair cost exceeds 50% of a replacement, consider recycling responsibly."
        ),
        "score": 7
    },
    "3 beeps": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: The computer beeps 3 times, pauses, and beeps 3 times again in a repeating loop.\n"
            "What it means: The computer found the memory (RAM), but the memory is failing its safety checks. The RAM chips are damaged beyond use.\n"
            "What to do: This usually means the memory is broken and will need a professional repair or replacement memory sticks. Take it to an Authorized Apple Service Provider for repair, or consider recycling if the cost is prohibitive — memory replacements on newer Macs can be very expensive."
        ),
        "score": 8
    },
    "sos beeps": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: The computer beeps 3 quick times, 3 long times, and 3 quick times (like an SOS signal).\n"
            "What it means: Your Mac's core software (firmware) is broken, and it is requesting help to restore itself. The good news is this is a software problem, not a physical hardware failure.\n"
            "What to do: Plug the Mac into its charger and leave it alone for up to 5 minutes — it may fix itself automatically. If it does not, take it to an Authorized Apple Service Provider where they can connect it to another Mac to revive the firmware. This repair is usually free or low-cost."
        ),
        "score": 6
    },
    "flexgate": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: The screen only lights up when the laptop is barely open, or the bottom of the screen has uneven bright spots that look like stage lights.\n"
            "What it means: A very fragile ribbon cable that connects the screen to the motherboard is tearing from repeatedly opening and closing the laptop. This is a known manufacturing defect on 2016–2018 MacBook Pro models.\n"
            "What to do: This requires a hardware repair — the entire display assembly typically needs to be replaced. Take it to an Authorized Apple Service Provider for a quote. Apple may cover certain models under a repair program, so ask about eligibility before paying."
        ),
        "score": 7
    },
    "fan spin no chime": {
        "response": (
            "MacBook Issue Found:\n\n"
            "What's happening: The fans spin at full speed, but the screen stays completely black and there is no startup sound.\n"
            "What it means: The main logic board cannot communicate with its temperature sensors, so it runs the fans at maximum speed as a safety measure and refuses to boot. This is almost always caused by liquid damage.\n"
            "What to do: This is usually caused by liquid short-circuiting a sensor (often in the trackpad or camera cable area). It needs professional cleaning and micro-soldering repair. If the repair cost exceeds 50% of a comparable replacement, consider recycling the device responsibly through Apple Trade In or a certified e-waste facility."
        ),
        "score": 9
    },

    # ==========================================
    # IOS RESTORE & FLASHING ERRORS (iTUNES)
    # ==========================================
    "error 4013": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The phone is stuck restarting over and over, or gives Error 4013 when plugged into a computer.\n"
            "What it means: A broken internal part is interrupting the phone's startup process. Most commonly, the earpiece speaker at the top of the screen has gotten wet and is short-circuiting.\n"
            "What to do: A repair shop can unplug the faulty part to get the phone to turn on and save your data. A replacement earpiece speaker is a relatively cheap and quick repair — usually under $50 at an independent shop. No need to recycle this device."
        ),
        "score": 4
    },
    "error 9": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: When trying to update or restore via a computer, it immediately fails with Error 9.\n"
            "What it means: The phone suddenly disconnected from the computer, OR the internal storage chip (NAND) has completely died.\n"
            "What to do: First, try a different high-quality USB cable and a different USB port. If it still fails, the internal storage chip is dead and requires very advanced motherboard micro-soldering repair. Take it to an Authorized Apple Service Provider or specialist repair shop for a quote. If repair costs exceed the value of the phone, consider recycling through Apple Trade In."
        ),
        "score": 9
    },
    "error 14": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The software update gets stuck partway through and then fails with Error 14.\n"
            "What it means: Your iPhone's storage is completely full, and there is no room left to install the update. The phone itself is not broken.\n"
            "What to do: The quickest fix is to erase the phone through a computer, which will delete your data. A professional repair shop may be able to use specialized software to update it without losing your photos. There is no need to recycle this device — the hardware is perfectly fine."
        ),
        "score": 4
    },
    "error 4014": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The phone briefly connects to the computer, shows Error 4014, and then immediately disconnects.\n"
            "What it means: This is a catastrophic hardware failure. The main processor (CPU) or memory chip on the motherboard is dead. Data recovery may not be possible.\n"
            "What to do: The phone is generally considered beyond economical repair. It requires extreme micro-soldering work to even attempt data recovery. Recycle the device responsibly through Apple Trade In or a certified e-waste recycler, and consider purchasing a comparable replacement."
        ),
        "score": 10
    },
    "error -1": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The software update reaches 99% and then fails with Error -1.\n"
            "What it means: The baseband chip — the part of the phone that connects to cellular towers — is broken or has lost its connection to the motherboard.\n"
            "What to do: The phone cannot verify its cellular radio, which Apple requires for activation. This requires advanced motherboard micro-soldering to repair the baseband chip. If repair costs exceed the phone's value, recycle the device through Apple Trade In and consider a replacement."
        ),
        "score": 10
    },

    # ==========================================
    # IOS HARDWARE & COMPONENT FAILURES
    # ==========================================
    "boot loop": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The Apple logo appears for a few seconds, the screen goes black, and it repeats this cycle forever.\n"
            "What it means: The phone is trying to turn on, checking all its internal parts, finding a broken one, and shutting itself down for safety. This is called a 'boot loop.'\n"
            "What to do: A repair shop will need to open the phone and systematically unplug parts one by one (cameras, charging port, sensors) until they find the one causing the crash. Once identified, that single part can usually be replaced affordably. Do not throw this phone away — it is very likely repairable."
        ),
        "score": 5
    },
    "panic full": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The iPhone randomly restarts itself while you are using it, without any warning.\n"
            "What it means: A tiny sensor inside the phone is malfunctioning, so the phone restarts itself as a protective measure. This is usually a minor hardware issue.\n"
            "What to do: A repair technician can read the phone's internal crash logs to pinpoint exactly which sensor is broken (most commonly the charging port or battery sensor) and replace just that part. This is typically an affordable repair — no need to replace the phone."
        ),
        "score": 3
    },
    "no face id": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The phone displays a message saying 'Face ID is not available.'\n"
            "What it means: The Face ID camera system is broken, usually from a tiny drop of water entering through the top earpiece speaker. The rest of the phone works perfectly fine.\n"
            "What to do: Face ID parts are security-paired to your specific phone, so a standard replacement will not work. A specialist repair shop can carefully transfer the serial data from your broken Face ID module to a new one. This is an advanced repair — get a quote first, as costs vary significantly between shops."
        ),
        "score": 8
    },
    "important battery message": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: You see a warning saying 'Unable to verify this iPhone has a genuine Apple battery.'\n"
            "What it means: A new battery was installed, but Apple's security system does not recognize it — even if it is a perfectly good battery. Your phone will continue to work normally.\n"
            "What to do: You can safely ignore this message; it does not affect performance or safety. If it bothers you, a repair shop can transfer the tiny authentication chip from your original battery onto the new one. This is the easiest possible fix — absolutely no reason to recycle or replace this device."
        ),
        "score": 1
    },
    "no service": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The phone says 'No Service' or 'Searching...' constantly, even in areas with strong signal.\n"
            "What it means: The internal baseband chip that communicates with cell towers has cracked or broken its connection to the motherboard. This is a well-known issue caused by dropping the phone or putting pressure on it (like sitting on it).\n"
            "What to do: This requires advanced motherboard micro-soldering to restore the baseband connection. Take it to a specialist repair shop for a quote. If the repair cost exceeds the phone's value, recycle through Apple Trade In and consider a replacement device."
        ),
        "score": 9
    },
    "pink screen": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The screen flashes bright pink for a moment before the phone restarts itself.\n"
            "What it means: The phone's graphics processing unit (GPU) crashed. If this happens once, it may just be a temporary glitch. If it happens repeatedly, the motherboard's graphics system is beginning to fail.\n"
            "What to do: First, try force-restarting the phone (press and quickly release Volume Up, then Volume Down, then hold the Power button until the Apple logo appears). If it keeps happening daily, the motherboard likely needs repair. Take it to an Authorized Apple Service Provider for diagnosis — if repair costs are high, consider recycling and upgrading."
        ),
        "score": 8
    },
    "ghost touch": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: The screen taps on things, scrolls, or types all by itself without you touching it.\n"
            "What it means: The touch digitizer layer inside the screen glass is damaged, usually from a drop or pressure crack (even if the glass looks fine on the outside).\n"
            "What to do: The fix is straightforward — simply replace the screen at any repair shop. This is one of the most common and affordable iPhone repairs. Do not throw this phone away; it is an easy fix."
        ),
        "score": 2
    },
    "green line": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: There is a bright, permanent green line running vertically down the screen that never goes away.\n"
            "What it means: The delicate driver electronics built into the edge of the OLED screen panel have broken, usually from impact damage. The motherboard and all other components are fine.\n"
            "What to do: The entire screen assembly needs to be replaced — this is a standard repair available at most shops. The phone is otherwise perfectly healthy, so there is no reason to recycle it."
        ),
        "score": 2
    },
    "unable to activate": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: During setup, the phone gets permanently stuck on 'Unable to Activate. An update is required.'\n"
            "What it means: Apple's activation servers cannot verify the phone because its internal cellular modem or NFC chip is completely dead. Apple will not allow the phone to be used until this is fixed.\n"
            "What to do: This requires advanced motherboard micro-soldering to repair the broken chips. If the repair cost exceeds the phone's value, recycle the device responsibly through Apple Trade In or a certified e-waste facility and purchase a comparable replacement."
        ),
        "score": 10
    },
    "audio ic disease": {
        "response": (
            "iPhone Issue Found:\n\n"
            "What's happening: People cannot hear you on phone calls, the Voice Memos app is greyed out, and the phone takes several minutes to boot up.\n"
            "What it means: A tiny solder connection between the audio processing chip and the motherboard has cracked. This is an extremely common defect on the iPhone 7 and 7 Plus, known in the repair community as 'Audio IC Disease.'\n"
            "What to do: A specialist repair shop needs to remove the audio chip from the motherboard, rebuild the broken connection with a thin wire (called a 'jumper'), and resolder the chip back on. This is a well-documented repair with high success rates — get a quote from a micro-soldering specialist before deciding."
        ),
        "score": 6
    }
}


@app.route("/about.html")
def about_page():
    return render_template("about.html")

@app.route("/", methods=["GET", "POST"])
def main_terminal():
    if request.method == "POST":
        device_type = request.form.get("device_type")
        user_question = request.form.get("user_question")
        
        api_response = None
        repairability_score = None
        
        if user_question in OFFLINE_DB:
            api_response = OFFLINE_DB[user_question]["response"]
            repairability_score = OFFLINE_DB[user_question]["score"]
        else:
            if user_question == "custom_cloud":
                user_question = request.form.get("custom_query")
                
            full_prompt = f"Device Architecture: {device_type}\nReported Symptom/Error: {user_question}"

            try:  
                chat_completion = client.chat.completions.create(
                    model="gemini-3-flash-preview",
                    messages=[
                        {"role": "system", "content": "You are a technical assistant for diagnosing hardware codes. Your task is to diagnose and provide solutions in a way that a non-technical person can understand. Provide these solutions in a short but concise evaluation of the error/problem. You must also evaluate a repairability score from 10 (impossible, total logic board replacement needed) to 0 (easy fix, basic software update or common part swap). You MUST return your ENTIRE output as a valid JSON object with EXACTLY two keys: 'response' containing your text evaluation, and 'score' containing the integer score."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                
                raw_content = chat_completion.choices[0].message.content.strip()
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:-3].strip()
                elif raw_content.startswith("```"):
                    raw_content = raw_content[3:-3].strip()
                    
                data = json.loads(raw_content)
                api_response = data.get("response", "Could not parse response.")
                repairability_score = data.get("score", 5)
                
            except Exception as e:
                api_response = f"There was an error, try again or contact support: {str(e)}"
                repairability_score = 0

        return jsonify({"response": api_response, "repairability_score": repairability_score})

    return render_template("frontend.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)