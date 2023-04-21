var startBtn=document.getElementById('startBtn');
var stopBtn=document.getElementById('stopBtn');
var result=document.getElementById("card-textarea");
var SubtitleStatus=document.getElementById("SubtitleStatus");
let languageSelect = document.getElementById("language");
var ldownloadTxtBtn = document.getElementById('ldownloadTxtBtn');
var ldownloadSrtBtn = document.getElementById('ldownloadSrtBtn');
const resetButton = document.querySelector('#resetButton');
var emailDialog = document.querySelector('#send_rec_email_model');
var sendMail=document.getElementById('sendMailBtn');
const messageDialog = document.querySelector('#message_dialog_modal');
startBtn.addEventListener("click", startRecording);
stopBtn.addEventListener("click", stopRecording);

var recognition = new webkitSpeechRecognition();
var rec;
final_transcript=""
recognition.continuous = true;
recognition.interimResults = true;
recognition.language="en-US"
window.onload=function(){
    let textAreaData = document.getElementById("card-textarea").value;
    if (textAreaData.trim()===""){
        try {
            ldownloadTxtBtn.style.display="none";
            ldownloadSrtBtn.style.display="none";
            resetButton.style.display="none";
            sendMail.style.display="none";
          } catch (error) {
            
          }
    }else{
        try {
            ldownloadTxtBtn.style.display="inline-block";
            ldownloadSrtBtn.style.display="inline-block";
            resetButton.style.display="inline-block";
            sendMail.style.display="inline-block";
          } catch (error) {
            
          }
    }
}
navigator
    .mediaDevices
    .getUserMedia({audio: true})
    .then(stream => { handlerFunction(stream) });;




function sendData(data) {
   
    
    
    let formData = new FormData();
    formData.append('audio', data, 'audio.wav');
    const fileSize = (data.size / 1024 / 1024).toFixed(2); // Convert to MB and round to 2 decimal places
    console.log(`The size of the audio file is ${fileSize} MB.`);
    SubtitleStatus.innerHTML="Generating Subtitles..."
    setTimeout(delayFunc, 20000);
    
        fetch("/upload", {
        method: "POST",
        body: formData
        })
        .then(response => response.text())
        .then(data => {
        result.innerHTML = data;
        try {
            ldownloadTxtBtn.style.display="inline-block";
                ldownloadSrtBtn.style.display="inline-block";
                resetButton.style.display="inline-block";
                sendMail.style.display="inline-block";
        } catch (error) {
            
        }
        SubtitleStatus.innerHTML="Subtitle Generated! Enjoy"; 
        })
        .catch(error => console.error(error));


        }


function startRecording() {
    console.log("Recording are started.");
    startBtn.style.display="none"
    stopBtn.style.display="inline-block"
    audioChunks = [];
    rec.start();
    recognition.start();

    
}
function openMessageDialog(){
  sendMail.classList.add('hidden');
  document.getElementById('back_message_dialog_modal').classList.remove('hidden');
}
function closeMessage() {
    location.href="/live";
  }
function stopRecording() {
    console.log("Recording are stopped.");
    startBtn.style.display="inline-block"
    stopBtn.style.display="none"
    rec.stop();
    recognition.stop();
}
function handlerFunction(stream) {
rec = new MediaRecorder(stream);
rec.ondataavailable = e => {
    audioChunks.push(e.data);
    if (rec.state == "inactive") {
        let blob = new Blob(audioChunks, {type: 'audio/wav'});
        sendData(blob);
    }
}
}
recognition.onresult = function(event) {
var interim_transcript = '';
for (var i = event.resultIndex; i < event.results.length; ++i) {
    if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;
    } else {
        interim_transcript += event.results[i][0].transcript;
        document.getElementById("card-textarea").innerHTML= final_transcript;
    }
}
document.getElementById("card-textarea").innerHTML= final_transcript;
};
result.addEventListener("contextmenu", function(event) {
event.preventDefault();
});
function openModal() {
document.getElementById('modal').classList.remove('hidden');

}

function closeModal() {
document.getElementById('modal').classList.add('hidden');
}
try{
    function closeMessageModal() {
        location.href="/live"
        }
}catch (error) {
    
}

function resetTextField() {
location.reload();


}
 function delayFunc() {
    DayPilot.Modal.confirm("File is seems to be big!\n Do you want to send as email or wait?",{theme:"modal_rounded", okText: "Sent via mail", cancelText: "I'll wait"})
    .then(function(args) {
        if (args.result) {
            document.getElementById("back_message_dialog_modal").classList.remove('hidden');
        fetch("/send-as-mail-audio-background", {
            method: "POST",
            body: formData
            })
        .then(response => response.text())
        .then(data => {
            
            })
        .catch(error => console.error(error));
    }
        else {
            fetch("/upload", {
                method: "POST",
                body: formData
                })
                .then(response => response.text())
                .then(data => {
                result.innerHTML = data;
                try {
                    ldownloadTxtBtn.style.display="inline-block";
                        ldownloadSrtBtn.style.display="inline-block";
                        resetButton.style.display="inline-block";
                        sendMail.style.display="inline-block";
                } catch (error) {
                    
                }
            });
            DayPilot.Modal.alert("You canceled the modal dialog.");
        }
    });
    

}