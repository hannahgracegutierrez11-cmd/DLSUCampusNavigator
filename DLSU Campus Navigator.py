import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

basePath = r"C:\Users\hcg\Downloads\Project Map"

#List of Rooms,Buildings, and Gates
def numRange(start, end):
    return [str(i) for i in range(start, end + 1)]

def letterRange(prefix, start, end):
    return [f"{prefix}{chr(i)}" for i in range(ord(start), ord(end) + 1)]

campusBuildings = {
    "Henry": (
        numRange(1401, 1419) +
        ["1201", "1202"] +
        letterRange("12", "A", "H") +
        ["1001", "1002"] +
        letterRange("10", "A", "H") +
        letterRange("9", "A", "H") +
        ["801", "802", "803"] +
        letterRange("8", "A", "H") +
        ["701"] +
        letterRange("7", "A", "H") +
        ["601", "602", "603", "coffee bean",
         "501", "502", "503"] +
        numRange(401, 407) +
        ["301", "301A", "302B", "303"] +
        numRange(201, 203)
    ),
    "Velasco": (
        numRange(501, 512) +
        ["401A", "401B", "402", "403A", "403B"] +
        numRange(404, 415) +
        ["301", "302", "303A", "303B"] +
        numRange(304, 313) +
        ["200A", "200B", "201A", "201B", "201C"] +
        numRange(202, 207) +
        ["208A", "208B", "101"] +
        letterRange("102", "A", "D") +
        numRange(103, 109)
    ),
    "Miguel": (
        ["401"] +
        letterRange("402", "A", "C") +
        numRange(403, 410) +
        numRange(301, 317) +
        numRange(201, 211) +
        ["212A", "212B"] +
        numRange(213, 215) +
        ["101A", "101B", "102", "103A", "103B"] +
        numRange(104, 114) +
        ["115A", "115B", "115C", "116"]
    )
}

buildingList = list(campusBuildings.keys())
gateList = ["Gate 1", "Gate 2"]

#Adjusts Room Options Depending on the Building
def updateRooms(event, buildingBox, roomBox):
    roomBox["values"] = campusBuildings.get(buildingBox.get(), [])
    roomBox.set("Select room")

#Displays Map Layout and Resizing the Image
def loadImage(path, label, maxWidth=800):
    if not os.path.exists(path):
        label.config(text="Map not found", image="")
        return

    img = Image.open(path)
    width, height = img.size
    scale = maxWidth / width
    img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)

    label.config(image=img, text="")
    label.image = img

#Displays Map with Route Lines
def showBuildingMap(start, end):
    folder = os.path.join(basePath, "Buildings")

    for file in os.listdir(folder):
        name = file.lower()
        if start.lower() in name and end.lower() in name and file.endswith(".png"):
            loadImage(os.path.join(folder, file), buildingMapLabel)
            return

    buildingMapLabel.config(text="No building route found", image="")

#Displays Room Layout
def showRoomMap(building, room):
    path = os.path.join(basePath, building, f"{room}.png")
    loadImage(path, roomMapLabel)

#Directions
def getDirections(start, end):
    match (start, end):
        case ("Gate 1", "Henry"):
            return "Walk through La Salle Hall until you reach Henry Sy Building"
        case ("Gate 1", "Velasco"):
            return "Walk through La Salle Hall and Henry Sy grounds until you reach Velasco"
        case ("Gate 2", "Velasco"):
            return "Upon entering, walk to your right side until you reach Velasco"
        case ("Henry", "Velasco"):
            return "From CADS, face Taft side and Velasco Hall would be on your left"
        case ("Henry", "Miguel"):
            return "Walk towards Velasco building along Bloemen side, and walk straight to Miguel"
        case ("Velasco", "Miguel"):
            return "Exit Velasco south exit and walk straight until Miguel Hall"
        case _:
            return "No specific directions available."

#Function to Extract Floor Number from Room Name
def getFloorFromRoom(room):
    if not room or room == "Select room":
        return None

    room = str(room).lower()

    if "coffee" in room:
        return 5

    digits = ""
    for char in room:
        if char.isdigit():
            digits += char
        else:
            break

    if digits == "":
        return None

    # FIXED: always correct floor extraction
    if len(digits) >= 4:
        return int(digits[:2])
    else:
        return int(digits[0])

#Choosing the Map to Display and the Output Text
def navigate():
    buildingMapLabel.config(image="", text="")
    roomMapLabel.config(image="", text="")
    outputBox.delete("1.0", tk.END)

    startGate = currentGate.get()
    startBuilding = currentBuilding.get()
    startRoom = currentRoom.get()
    endBuilding = targetBuilding.get()
    endRoom = targetRoom.get()

    startFloor = getFloorFromRoom(startRoom)
    endFloor = getFloorFromRoom(endRoom)


    # From Gate
    if startGate != "None":
        outputBox.insert(tk.END, f"{startGate} → {endBuilding}\n\n")


        directions = getDirections(startGate, endBuilding)
        outputBox.insert(tk.END, f"{directions}\n")


        if endFloor:
            outputBox.insert(tk.END,
                f"Then go up {endFloor} floor(s) via stairs and follow the floor map to Room {endRoom}\n")


        showBuildingMap(startGate, endBuilding)
        showRoomMap(endBuilding, endRoom)
        return


    #Same Building
    if startBuilding == endBuilding:
        if startFloor and endFloor:
            if startFloor > endFloor:
                outputBox.insert(tk.END,
                    f"Go down {startFloor - endFloor} floor(s) via stairs\n")
            elif startFloor < endFloor:
                outputBox.insert(tk.END,
                    f"Go up {endFloor - startFloor} floor(s) via stairs\n")
            else:
                outputBox.insert(tk.END,
                    f"You are already on the correct floor. Follow the floor map to Room {endRoom}\n")


        showRoomMap(endBuilding, endRoom)
        return
        
    #Building to Building
    outputBox.insert(tk.END, f"{startBuilding} → {endBuilding}\n\n")


    #Step 1: Go Down First
    if startFloor:
        outputBox.insert(tk.END,
            f"Go down {startFloor} floor(s) to reach the ground floor\n")


    #Step 2: Walk Between Buildings
    directions = getDirections(startBuilding, endBuilding)
    outputBox.insert(tk.END, f"{directions}\n")


    #Step 3: Go Up to Target Floor
    if endFloor:
        outputBox.insert(tk.END,
            f"Then go up {endFloor} floor(s) via stairs and follow the floor map to Room {endRoom}\n")


    showBuildingMap(startBuilding, endBuilding)
    showRoomMap(endBuilding, endRoom)

#GUI
rootWindow = tk.Tk()
rootWindow.title("Campus Navigator")
rootWindow.geometry("900x750")
rootWindow.configure(bg="#eef2f7")

#Scroll System
canvasArea = tk.Canvas(rootWindow, bg="#eef2f7", highlightthickness=0)
scrollBar = tk.Scrollbar(rootWindow, orient="vertical", command=canvasArea.yview)
scrollFrame = tk.Frame(canvasArea, bg="#eef2f7")

scrollFrame.bind("<Configure>", lambda e: canvasArea.configure(scrollregion=canvasArea.bbox("all")))

canvasArea.create_window((0, 0), window=scrollFrame, anchor="nw")

#Centering the Content in the Canvas
def centerContent(event):
    canvasWidth = event.width
    frameWidth = scrollFrame.winfo_reqwidth()

    x = max((canvasWidth - frameWidth) // 2, 0)
    canvasArea.coords(canvasWindow, x, 0)

#Store Window Reference
canvasWindow = canvasArea.create_window((0, 0), window=scrollFrame, anchor="nw")

#Bind Resize Event
canvasArea.bind("<Configure>", centerContent)
canvasArea.configure(yscrollcommand=scrollBar.set)

canvasArea.pack(side="left", fill="both", expand=True)
scrollBar.pack(side="right", fill="y")

#GUI Header
headerLabel = tk.Label(
    scrollFrame,
    text="Campus Navigator",
    font=("Segoe UI", 26, "bold"),
    bg="#eef2f7",
    fg="#1f2937"
)
headerLabel.pack(pady=(20, 5))

subtitleLabel = tk.Label(
    scrollFrame,
    text="Ready to explore the DLSU?",
    font=("Segoe UI", 11),
    bg="#eef2f7",
    fg="#6b7280"
)
subtitleLabel.pack(pady=(0, 20))

#Card That Contains The Inputs and Outputs
cardFrame = tk.Frame(scrollFrame, bg="white", bd=0)
cardFrame.pack(padx=30, pady=10)

innerFrame = tk.Frame(cardFrame, bg="white")
innerFrame.pack(padx=20, pady=20)

innerFrame.columnconfigure(0, weight=1)
innerFrame.columnconfigure(1, weight=1)

#Dropdown Style
style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", padding=8)

#Input System
def createLabel(text, row, col):
    tk.Label(innerFrame, text=text, bg="white",
             font=("Segoe UI", 10, "bold"),
             fg="#374151").grid(row=row, column=col, sticky="w", pady=(5,2))

createLabel("🚪 Start from Gate", 0, 0)
currentGate = ttk.Combobox(innerFrame, values=["None"] + gateList, state="readonly")
currentGate.grid(row=1, column=0, sticky="ew")
currentGate.set("None")

createLabel("📍 Current Building", 2, 0)
currentBuilding = ttk.Combobox(innerFrame, values=buildingList, state="readonly")
currentBuilding.grid(row=3, column=0, sticky="ew")

createLabel("Current Room", 2, 1)
currentRoom = ttk.Combobox(innerFrame, state="readonly")
currentRoom.grid(row=3, column=1, sticky="ew")

createLabel("📌 Target Building", 4, 0)
targetBuilding = ttk.Combobox(innerFrame, values=buildingList, state="readonly")
targetBuilding.grid(row=5, column=0, sticky="ew")

createLabel("Target Room", 4, 1)
targetRoom = ttk.Combobox(innerFrame, state="readonly")
targetRoom.grid(row=5, column=1, sticky="ew")

#Update Room Options Based on Building Selected
currentBuilding.bind("<<ComboboxSelected>>",
    lambda e: updateRooms(e, currentBuilding, currentRoom))
targetBuilding.bind("<<ComboboxSelected>>",
    lambda e: updateRooms(e, targetBuilding, targetRoom))

#Button to Start Navigation
tk.Button(innerFrame,
          text="Navigate",
          bg="#4f46e5",
          fg="white",
          font=("Segoe UI", 11, "bold"),
          relief="flat",
          padx=10,
          pady=8,
          command=navigate).grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")

#Output (Instructions)
outputBox = tk.Text(innerFrame, height=5, bg="#f9fafb", relief="flat")
outputBox.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")

#Output (Maps)
buildingMapLabel = tk.Label(innerFrame, bg="white")
buildingMapLabel.grid(row=8, column=0, columnspan=2, pady=10)

roomMapLabel = tk.Label(innerFrame, bg="white")
roomMapLabel.grid(row=9, column=0, columnspan=2, pady=10)

#Keep the Window Running
rootWindow.mainloop()