# Libraries required
import os
from tkinter import *
import tkinter as tk
from geopy.geocoders import Nominatim
from tkinter import ttk, messagebox
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz

# for images path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize the main application window
root = Tk()
root.title("Weather App")
root.geometry("900x500+300+200") 
root.resizable(False, False) 

# Function to fetch and display weather information
def getweather():
    try:
       city = textfield.get() 

       # Convert city name to geographical coordinates
       geolocator = Nominatim(user_agent="weather-app-shj4185669@gmail.com")
       location = geolocator.geocode(city)

       if location:
          # Find timezone based on coordinates
          obj = TimezoneFinder()
          result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
          print("Timezone:",result)
       
          # Get current local time of the city
          home = pytz.timezone(result)
          local_time = datetime.now(home)
          current_time = local_time.strftime("%I:%M:%p")

          # Update time and title label
          clock.config(text=current_time)
          name.config(text="CURRENT WEATHER")

          # Fetch weather data using OpenWeatherMap API
          api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=66a737da5342fdaf139eef32301aa625&units=metric"
          json_data = requests.get(api).json()

          # Extract required data from API response
          condition = json_data['weather'][0]['main']
          description = json_data['weather'][0]['description']
          temp = round(json_data['main']['temp'], 1)
          pressure = json_data['main']['pressure']
          humidity = json_data['main']['humidity']
          wind = json_data['wind']['speed']

          # Update weather info labels on GUI
          t.config(text=f"{temp}°C")
          c.config(text=f"{condition} | FEELS LIKE {temp}°C")

          wind_kmh = round(wind * 3.6, 1)
          w.config(text=f"{wind_kmh} km/h")
          h.config(text=f"{humidity}%")
          d.config(text=description.capitalize())
          p.config(text=f"{pressure} hPa")
       else:
           messagebox.showerror("Error", "Invalid city name. Please try again.")
           return
                                        
    except Exception as e:
        messagebox.showerror("weather App", "Invalid Entry\nPlease try again.\nError: " + str(e))

# Load and place GUI images and elements
Search_image = PhotoImage(file=os.path.join(BASE_DIR, "assets", "search.png"))
myimage = Label(image=Search_image)
myimage.place(x=20, y=20)

textfield = tk.Entry(root, justify="center", width=17, font=("poppins", 25, "bold"),bg="#404040", border=0, fg="white")
textfield.place(x=50, y=40)
textfield.focus()

Search_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets", "search_icon.png"))
myimage_icon = Button(image=Search_icon, borderwidth=0, cursor="hand2", bg ="#404040",command=getweather)
myimage_icon.place(x=400, y=34)

Logo_image = PhotoImage(file=os.path.join(BASE_DIR, "assets", "logo.png"))
logo = Label(image=Logo_image)
logo.place(x=150, y=100)

Frame_image = PhotoImage(file=os.path.join(BASE_DIR, "assets", "box.png"))
frame_myimage = Label(image=Frame_image)
frame_myimage.pack(padx=5, pady=5, side=BOTTOM)

# Clock and city label
name = Label(root, font=("arial", 15, "bold"))
name.place(x=30, y=100)
clock = Label(root, font=("Helvetica", 20))
clock.place(x=30, y=130)

# Weather parameter labels
label1 = Label(root, text="WIND", font=("Helvetica", 15, "bold"), fg="white", bg="#1ab5ef")
label1.place(x=120, y=400)

label2 = Label(root, text="HUMIDITY", font=("Helvetica", 15, "bold"), fg="white", bg="#1ab5ef")
label2.place(x=250, y=400)

label3 = Label(root, text="DESCRIPTION", font=("Helvetica", 15, "bold"), fg="white", bg="#1ab5ef")
label3.place(x=430, y=400)

label4 = Label(root, text="PRESSURE", font=("Helvetica", 15, "bold"), fg="white", bg="#1ab5ef")
label4.place(x=650, y=400)

# Dynamic labels for displaying weather values
t = Label(font=("arial", 70, "bold"), fg="#ee666d")
t.place(x=400, y=150)
c = Label(font=("arial", 15, "bold"))
c.place(x=400, y=250)

w = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
w.place(x=120, y=430)
h = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
h.place(x=280, y=430)
d = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
d.place(x=400, y=430)
p = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
p.place(x=650, y=430)

# Start the application
root.mainloop()