import os
import socket
import time
from datetime import datetime, timedelta
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from timezonefinder import TimezoneFinder
import requests
import pytz
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Weather Forecast App")
root.geometry("890x470+300+200")
root.configure(bg="#57adff")
root.resizable(False, False)

# Complete weather code mapping with detailed descriptions
WEATHER_ICONS = {
    0: ("01d", "01n"),      # Clear sky
    1: ("02d", "02n"),      # Mostly clear
    2: ("03d", "03n"),      # Partly cloudy
    3: ("04d", "04n"),      # Overcast
    45: ("50d", "50n"),     # Fog
    48: ("50d", "50n"),     # Freezing fog
    51: ("09d", "09n"),     # Drizzle
    53: ("09d", "09n"),     # Drizzle
    55: ("09d", "09n"),     # Drizzle
    56: ("13d", "13n"),     # Freezing drizzle
    57: ("13d", "13n"),     # Freezing drizzle
    61: ("10d", "10n"),     # Rain
    63: ("10d", "10n"),     # Rain
    65: ("10d", "10n"),     # Rain
    66: ("13d", "13n"),     # Freezing rain
    67: ("13d", "13n"),     # Freezing rain
    71: ("13d", "13n"),     # Snow
    73: ("13d", "13n"),     # Snow
    75: ("13d", "13n"),     # Snow
    77: ("13d", "13n"),     # Snow grains
    80: ("09d", "09n"),     # Rain showers
    81: ("09d", "09n"),     # Rain showers
    82: ("09d", "09n"),     # Rain showers
    85: ("13d", "13n"),     # Snow showers
    86: ("13d", "13n"),     # Snow showers
    95: ("11d", "11n"),     # Thunderstorm
    96: ("11d", "11n"),     # Thunderstorm with hail
    99: ("11d", "11n")      # Thunderstorm with hail
}

def get_weather_description(code):
    """Convert weather code to detailed text description"""
    weather_map = {
        0: "Clear sky",
        1: "Mostly clear", 
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Freezing fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        56: "Light freezing drizzle",
        57: "Heavy freezing drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Light rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        85: "Light snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with light hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_map.get(code, "Unknown weather condition")

def is_internet_available():
    """Check if internet connection is available"""
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False

def get_location_with_retry(geolocator, city, max_retries=3):
    """Get location with retry logic for timeouts"""
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(city)
            if location:
                return location
        except GeocoderTimedOut:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)  # wait before retrying
    return None

def getWeather():
    city = textfield.get()
    if not city:
        messagebox.showerror("Error", "Please enter a city name")
        return

    if not is_internet_available():
        messagebox.showerror("Error", "No internet connection available")
        return

    try:
        geolocator = Nominatim(user_agent="WeatherForecastApp", timeout=10)
        location = get_location_with_retry(geolocator, city)
        
        if location is None:
            messagebox.showerror("Error", "City not found")
            return
            
        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
        timezone.config(text=result)
        long_lat.config(text=f"{round(location.latitude, 4)}°N, {round(location.longitude, 4)}°E")

        home = pytz.timezone(result)
        local_time = datetime.now(home)
        current_time = local_time.strftime("%I:%M %p")
        clock.config(text=current_time)

        # Get weather data with retry
        for attempt in range(3):
            try:
                api = f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&current_weather=true&hourly=relativehumidity_2m,pressure_msl,is_day&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=auto&forecast_days=8"
                json_data = requests.get(api, timeout=10).json()
                break
            except requests.exceptions.RequestException:
                if attempt == 2:
                    raise
                time.sleep(1)

        current = json_data['current_weather']
        temp = current['temperature']
        wind = current['windspeed']
        weather_code = current['weathercode']
        is_day = current['is_day']
        description = get_weather_description(weather_code)

        hourly = json_data['hourly']
        humidity = hourly['relativehumidity_2m'][0]
        pressure = hourly['pressure_msl'][0]

        t.config(text=(f"{temp}°C"))
        h.config(text=(f"{humidity}%"))
        p.config(text=(f"{pressure} hPa"))
        w.config(text=(f"{wind} m/s"))
        d.config(text=description)

        daily = json_data['daily']
        weather_codes = daily['weathercode']
        temp_max = daily['temperature_2m_max']
        temp_min = daily['temperature_2m_min']
        sunrises = daily['sunrise']
        sunsets = daily['sunset']

        # Current weather icon
        first_day_icon = WEATHER_ICONS.get(weather_code, ("04d", "04n"))[0 if is_day else 1]
        try:
            photo1 = ImageTk.PhotoImage(file=os.path.join(BASE_DIR, "assets", "icon", f"{first_day_icon}@2x.png"))
            firstimage.config(image=photo1)
            firstimage.image = photo1
        except Exception as e:
            print(f"Error loading image: {e}")

        day1.config(text="Today")
        day1temp.config(text=f"Day: {temp_max[0]}°C\nNight: {temp_min[0]}°C")

        # Forecast days
        now = datetime.now(home).time()
        
        for i in range(1, 7):
            frame = [secondframe, thirdframe, fourthframe, fifthframe, sixthframe, seventhframe][i-1]
            day_label = [day2, day3, day4, day5, day6, day7][i-1]
            image_label = [secondimage, thirdimage, fourthimage, fifthimage, sixthimage, seventhimage][i-1]
            temp_label = [day2temp, day3temp, day4temp, day5temp, day6temp, day7temp][i-1]
            
            day_name = (datetime.now() + timedelta(days=i)).strftime("%A")[:3]
            day_label.config(text=day_name)
            temp_label.config(text=f"Day: {temp_max[i]}°C\nNight: {temp_min[i]}°C")
            
            # Get appropriate icon
            try:
                sunrise = datetime.strptime(sunrises[i], "%Y-%m-%dT%H:%M").time()
                sunset = datetime.strptime(sunsets[i], "%Y-%m-%dT%H:%M").time()
                is_daytime = sunrise <= now <= sunset
            except:
                is_daytime = True
            
            dayimage = WEATHER_ICONS.get(weather_codes[i], ("04d", "04n"))[0 if is_daytime else 1]
            
            try:
                img = Image.open(os.path.join(BASE_DIR, "assets", "icon", f"{dayimage}@2x.png"))
                resized_img = img.resize((50, 50))
                photo = ImageTk.PhotoImage(resized_img)
                image_label.config(image=photo)
                image_label.image = photo
            except Exception as e:
                print(f"Error loading image for day {i}: {e}")

    except requests.exceptions.RequestException:
        messagebox.showerror("Error", "Weather service unavailable. Please try again later.")
    except GeocoderTimedOut:
        messagebox.showerror("Error", "Geocoding service timed out. Please try again.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get weather data: {str(e)}")

# GUI Setup (same as before)
# icon 
image_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets/Images/logo.png"))
root.iconphoto(False, image_icon)

Round_box = PhotoImage(file=os.path.join(BASE_DIR, "assets/Images/Rounded Rectangle 1.png"))
Label(root, image=Round_box, bg="#57adff").place(x=30, y=110)

# label
label1 = Label(root, text="Temperature",font = ('Helvetica',11), fg = "white", bg="#203243")
label1.place(x=50, y=120)

label2 = Label(root, text="Humidity", font = ('Helvetica',11), fg = "white", bg="#203243")
label2.place(x=50, y=140)

label3 = Label(root, text="Pressure", font = ('Helvetica',11), fg = "white", bg="#203243")
label3.place(x=50, y=160)

label4 = Label(root, text="Wind Speed", font = ('Helvetica',11), fg = "white", bg="#203243")
label4.place(x=50, y=180)

label5 = Label(root, text="Description", font = ('Helvetica',11), fg = "white", bg="#203243")
label5.place(x=50, y=200)

# search box
Search_image = PhotoImage(file=os.path.join(BASE_DIR, "assets/Images/Rounded Rectangle 3.png"))
myimage = Label(image = Search_image, bg="#57adff")
myimage.place(x=270, y=120)

weat_image = PhotoImage(file=os.path.join(BASE_DIR, "assets/Images/Layer 7.png"))
weatherimage = Label(root,image = weat_image, bg="#203243")
weatherimage.place(x=290, y=127)

textfield = tk.Entry(root, justify="center", width=15, font=("poppins", 25, "bold"),bg="#203243",border = 0,fg = "white")
textfield.place(x=370, y=130)
textfield.focus()

Search_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets/Images/Layer 6.png"))
myimage_icon = Button(image = Search_icon, borderwidth = 0, cursor="hand2", bg ="#203243",command = getWeather)
myimage_icon.place(x=645, y=125)

# Bottom box
frame = Frame(root, width=900, height=180, bg="#212120")
frame.pack(side=BOTTOM)

# bottom boxes
firstbox = PhotoImage(file=os.path.join(BASE_DIR, "assets/Images/Rounded Rectangle 2.png"))
secondbox = PhotoImage(file=os.path.join(BASE_DIR, "assets/Images/Rounded Rectangle 2 copy.png"))

Label(frame,image= firstbox, bg="#212120").place(x=30,y=20)
Label(frame,image= secondbox, bg="#212120").place(x=300,y=30)
Label(frame,image= secondbox, bg="#212120").place(x=400,y=30)
Label(frame,image= secondbox, bg="#212120").place(x=500,y=30)
Label(frame,image= secondbox, bg="#212120").place(x=600,y=30)
Label(frame,image= secondbox, bg="#212120").place(x=700,y=30)
Label(frame,image= secondbox, bg="#212120").place(x=800,y=30)

# clock (here we will place time)
clock = Label(root, font = ("Helvetica",30,"bold"), fg = "white", bg="#57adff")
clock.place(x=30, y=20)

# timezone
timezone = Label(root, font = ("Helvetica",20),fg = "white", bg="#57adff")
timezone.place(x=700, y=20)

long_lat = Label(root, font = ("Helvetica",10),fg = "white", bg="#57adff")
long_lat.place(x=700, y=50)

# thpwd
t = Label(root,font = ("Helvetica",11),fg = "white",bg = "#203243")
t.place(x=150,y=120)
h = Label(root,font = ("Helvetica",11),fg = "white",bg = "#203243")
h.place(x=150,y=140)
p = Label(root,font = ("Helvetica",11),fg = "white",bg = "#203243")
p.place(x=150,y=160)
w = Label(root,font = ("Helvetica",11),fg = "white",bg = "#203243")
w.place(x=150,y=180)
d = Label(root,font = ("Helvetica",11),fg = "white",bg = "#203243")
d.place(x=150,y=200)

# first cell
firstframe = Frame(root, width=230, height=132, bg="#282829")
firstframe.place(x = 35,y = 315)

day1 = Label(firstframe, font = "arial 20", bg = "#282829",fg = "#fff")
day1.place(x = 140, y = 20, anchor="center")  # Centered

firstimage = Label(firstframe, bg = "#282829")
firstimage.place(x = 1, y = 15)

day1temp = Label(firstframe, bg = "#282829",fg = "#57adff",font = "arial 15 bold")
day1temp.place(x = 100,y = 50)

# second cell
secondframe = Frame(root, width=70, height=115, bg="#282829")
secondframe.place(x = 305, y = 325)

day2 = Label(secondframe, bg = "#282829",fg = "#fff", font=("Arial", 10, "bold"))
day2.place(x = 35, y = 15, anchor="center")  # Centered

secondimage = Label(secondframe, bg = "#282829")
secondimage.place(x = 10, y = 25)

day2temp = Label(secondframe, bg = "#282829",fg = "#fff", font=("Arial", 8))
day2temp.place(x = 35, y = 80, anchor="center")  # Centered

# third cell
thirdframe = Frame(root, width=70, height=115, bg="#282829")
thirdframe.place(x = 405, y = 325)

day3 = Label(thirdframe, bg = "#282829",fg = "#fff", font=("Arial", 10, "bold"))
day3.place(x = 35, y = 15, anchor="center")  # Centered

thirdimage = Label(thirdframe, bg = "#282829")
thirdimage.place(x = 10, y = 25)

day3temp = Label(thirdframe, bg = "#282829",fg = "#fff", font=("Arial", 8))
day3temp.place(x = 35, y = 80, anchor="center")  # Centered

# fourth cell
fourthframe = Frame(root, width=70, height=115, bg="#282829")
fourthframe.place(x = 505, y = 325)

day4 = Label(fourthframe, bg = "#282829",fg = "#fff", font=("Arial", 10, "bold"))
day4.place(x = 35, y = 15, anchor="center")  # Centered

fourthimage = Label(fourthframe, bg = "#282829")
fourthimage.place(x = 10, y = 25)

day4temp = Label(fourthframe, bg = "#282829",fg = "#fff", font=("Arial", 8))
day4temp.place(x = 35, y = 80, anchor="center")  # Centered

# fifth cell
fifthframe = Frame(root, width=70, height=115, bg="#282829")
fifthframe.place(x = 605, y = 325)

day5 = Label(fifthframe, bg = "#282829",fg = "#fff", font=("Arial", 10, "bold"))
day5.place(x = 35, y = 15, anchor="center")  # Centered

fifthimage = Label(fifthframe, bg = "#282829")
fifthimage.place(x = 10, y = 25)

day5temp = Label(fifthframe, bg = "#282829",fg = "#fff", font=("Arial", 8))
day5temp.place(x = 35, y = 80, anchor="center")  # Centered

# sixth cell
sixthframe = Frame(root, width=70, height=115, bg="#282829")
sixthframe.place(x = 705, y = 325)

day6 = Label(sixthframe, bg = "#282829",fg = "#fff", font=("Arial", 10, "bold"))
day6.place(x = 35, y = 15, anchor="center")  # Centered

sixthimage = Label(sixthframe, bg = "#282829")
sixthimage.place(x = 10, y = 25)

day6temp = Label(sixthframe, bg = "#282829",fg = "#fff", font=("Arial", 8))
day6temp.place(x = 35, y = 80, anchor="center")  # Centered

# seventh cell
seventhframe = Frame(root, width=70, height=115, bg="#282829")
seventhframe.place(x = 805, y = 325)

day7 = Label(seventhframe, bg = "#282829",fg = "#fff", font=("Arial", 10, "bold"))
day7.place(x = 35, y = 15, anchor="center")  # Centered

seventhimage = Label(seventhframe, bg = "#282829")
seventhimage.place(x = 10, y = 25)

day7temp = Label(seventhframe, bg = "#282829",fg = "#fff", font=("Arial", 8))
day7temp.place(x = 35, y = 80, anchor="center")  # Centered

root.mainloop()