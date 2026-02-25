from my_token import my_token as token

import requests
import tkinter as tk

def get_project():
    query = entry.get().lower()
    
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"per_page": 100, "sort": "updated"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            repos = response.json()

            filtered = [r for r in repos if query in r['name'].lower()]
            if not filtered:
                label_result.config(text="Репозиторий с таким названием не найден")
                return
            
            result = ""
            for repo in filtered:
                owner = repo['owner']['login']
                name = repo['name']

                result += f"Название: {name}\n"
                result += f"Приватный: {repo['private']}\n"
                result += f"Stars: {repo['stargazers_count']}\n"
                result += f"Язык: {repo['language'] or 'Нет данных'}\n"
                result += f"Описание: {repo['description'] or 'Нет данных'}\n"

                #Внизу получение закрытых данных доступные только по токену владельца

                #Получение распределения языков
                langs_r = requests.get(f"https://api.github.com/repos/{owner}/{name}/languages", headers=headers)
                if langs_r.status_code == 200:
                    langs = langs_r.json()
                    total = sum(langs.values()) or 1
                    langs_str = ", ".join(f"{l}: {b*100/total:.1f}%" for l, b in langs.items())
                    result += f"Языки: {langs_str}\n"

                #Статистика просмотров
                views_r = requests.get(f"https://api.github.com/repos/{owner}/{name}/traffic/views", headers=headers)
                if views_r.status_code == 200:
                    views = views_r.json()
                    result += f"Просмотры (14д): {views['count']} (уникальных {views['uniques']})\n"

                #Статистика клонов
                clones_r = requests.get(f"https://api.github.com/repos/{owner}/{name}/traffic/clones",headers=headers)
                if clones_r.status_code == 200:
                    clones = clones_r.json()
                    result += f"Клоны (14д): {clones['count']} (уникальных {clones['uniques']})\n"

            label_result.config(text=result)
        else:
            label_result.config(text=f"Ошибка: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        label_result.config(text="Нет подключения к интернету")
    except Exception as e:
        label_result.config(text=f"Ошибка: {e}")
        


window = tk.Tk()
window.title("Статистика гит хаб")
window.geometry("500x500")

text = tk.Label(window, text="Введите название репозитория", justify="left",font=("Arial", 18))
text.pack(pady=10)

entry = tk.Entry(window, width=30,font=("Arial", 18))
entry.pack(pady=20)


button = tk.Button(window, text="Получить",font=("Arial", 18), command=get_project)
button.pack(pady=10)


label_result = tk.Label(window, text="", justify="left",font=("Arial", 18))
label_result.pack(pady=10)

window.mainloop()