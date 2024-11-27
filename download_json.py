import requests

def download_json():
    url = "http://www.jma.go.jp/bosai/common/const/area.json"
    file_name = "area.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"ダウンロード完了: {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    download_json()
