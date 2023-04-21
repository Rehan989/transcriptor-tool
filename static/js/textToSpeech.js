const form = document.getElementById('upload-form');

const output = document.getElementById('filestatus');

const textarea = document.getElementById('content');

const downloadBtn = document.getElementById('downloadBtn');

const ldownloadSrtBtn = document.getElementById('ldownloadSrtBtn');

const ldownloadEngSrtBtn = document.getElementById('ldownloadEngSrtBtn');

const downloadTxtBtn = document.getElementById('downloadTxtBtn');

const downloadSrtBtn = document.getElementById('downloadSrtBtn');

const uploadStatus = document.getElementById('uploadStatus');
var uploadStatuscontent = "";

const uploadBtnDiv = document.getElementsByClassName('uploadBtnDiv');

const loginBtn = document.getElementById('loginBtn');
const audio = document.getElementById('audio');
const audioSource = document.getElementById('audioSource');

const fileInput = document.querySelector('#audio-file');
const textInput = document.querySelector('#content');

const fileLabel = document.querySelector('#file-label span:first-of-type');

const resetButton = document.querySelector('#resetButton');

const sendMail = document.querySelector('#sendMail');

const messageDialog = document.querySelector('#message_dialog_modal');

const backmessageDialog = document.querySelector('#back_message_dialog_modal');

var fsize = "";

window.onload = function () {

    downloadBtn.style.display = "none";

    resetButton.style.display = "none";

    sendMail.style.display = "none";


}

try {





    form.addEventListener('submit', (event) => {



        event.preventDefault();



        output.style.display = 'inline-block';

        uploadStatus.innerHTML = "Uploading..."

        document.getElementById("lottie_modal").classList.remove('hidden');

        const formData = new FormData(form);

        fetch('/process_text', {

            method: 'POST',

            body: formData,



        })

            .then(response => response.json())

            .then(data => {

                output.style.display = 'none';

                try {



                    downloadBtn.style.display = "inline-block";

                    ldownloadSrtBtn.style.display = "inline-block";

                    ldownloadEngSrtBtn.style.display = "inline-block";

                    resetButton.style.display = "inline-block";

                    sendMail.style.display = "inline-block";

                } catch (error) {

                    console.log(error)

                }



                uploadStatus.innerHTML = uploadStatuscontent;

                document.getElementById("lottie_modal").classList.add('hidden');

                audio.style.display = "inline-block";
                
                audioSource.src = `static/uploads/${data.file_name}`;

                document.getElementById("audioElem").load()
                document.getElementById("sendToEmail").style.display = 'inline-block'
                document.getElementById("sendToEmail").setAttribute('href', `/send-to-email/${data.file_name}`)


            })

            .catch(error => {

                uploadStatus.innerHTML = "Upload"

                console.error(error);

                output.innerHTML = 'Something Went wrong! Reload the Page';

                document.getElementById("lottie_modal").classList.add('hidden');

            });

    });



}





catch (error) {

    console.log(error);

}

function openModal() {

    document.getElementById('modal').classList.remove('hidden');

    let textAreaData = document.getElementById("card-textarea").value;

    localStorage.setItem("textareaData", textAreaData);



}

function openMessageDialog() {

    document.getElementById('send_email_model').classList.add('hidden');

    document.getElementById('back_message_dialog_modal').classList.remove('hidden');

}



function closeModal() {

    document.getElementById('modal').classList.add('hidden');

}

try {

    function closeMessageModal() {

        location.href = "/";

    }

} catch (error) {

    console.log(error)

}





function copyToClipboard() {



    navigator.clipboard.writeText(textarea.value);

}



textarea.addEventListener("contextmenu", function (event) {

    event.preventDefault();

});

fileInput.addEventListener('change', function (event) {
    if (fileInput.value) {
        uploadStatus.style.display = 'inline-block';

        uploadStatus.style.justifyContent = 'center';
        uploadStatuscontent = "Upload File"
        uploadStatus.innerText = uploadStatuscontent;
    }

    else {

        uploadStatus.style.display = 'none';

    }

});

textInput.addEventListener('change', function (event) {
    console.log(textInput.value)
    if (textInput.value !== "") {
        uploadStatus.style.display = 'inline-block';

        uploadStatuscontent = "Upload Text";
        uploadStatus.innerText = uploadStatuscontent;

    }

    else {
        uploadStatus.style.display = 'none';

    }

});



function autoSize(textarea) {

    textarea.style.height = 'auto';

    textarea.style.height = '${textarea.scrollHeight}px';





}

function resetTextField() {

    location.reload();





}

