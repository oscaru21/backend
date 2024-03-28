"use strict";

const serverUrl = "http://127.0.0.1:8000";

async function uploadFile() {
    let file = document.getElementById("file").files[0];
    let converter = new Promise(
        function(resolve, reject){
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(
                reader.result.toString().replace(/^data:(.*,)?/, '')
            );
            reader.onerror = (error) => reject(error);
        }
    );
    let encodedString = await converter;
    document.getElementById("file").value = "";

    // make server call to upload image
    // and return the server upload promise
    return fetch(serverUrl + "/audios", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({filename: file.name, filebytes: encodedString})
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new HttpError(response);
        }
    })

}

async function saveItem() {
    var currentDate = new Date();
    var year = currentDate.getFullYear();
    var month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
    var day = currentDate.getDate().toString().padStart(2, '0');
    var formattedDate = year + "-" + month + "-" + day;
    var hour = currentDate.getHours().toString().padStart(2, '0');
    var minute = currentDate.getMinutes().toString().padStart(2, '0');
    var second = currentDate.getSeconds().toString().padStart(2, '0');
    var formattedTime = hour + ":" + minute + ":" + second;
    var user = 'user01';
    var original_language = 'es';
    var original_transcript = 'Hola, como estas?';
    var translated_language = 'en';
    var translated_transcript = 'Hi, how are you?';
    var audio_file_path = '/path/to/audio/file';
    var category = 'testing';

    let item ={
        'id': formattedDate + formattedTime + user,
        'date': formattedDate,
        'time': formattedTime,
        'username': user,
        'original_language': original_language,
        'original_transcript': original_transcript,
        'translated_language': translated_language,
        'translated_transcript': translated_transcript,
        'audio_file_path': audio_file_path,
        'category': category
    }
    return fetch(serverUrl + "/save_meeting", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(item)

    }).then(response => {
        if (response.ok) {
            let res = response.json();
            console.log(res);
            return res;
        } else {
            throw new HttpError(response);
        }
    })
}

async function getMeetings() {
    return fetch(serverUrl + "/get_meetings", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"username": 'user01'})
    }).then(response => {
        if (response.ok) {
            let res = response.json();
            console.log(res);
            return res;
        } else {
            throw new HttpError(response);
        }
    })
}