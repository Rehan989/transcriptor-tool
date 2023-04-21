      const form = document.getElementById('upload-form');

      const output = document.getElementById('filestatus');

      const textarea = document.getElementById('card-textarea');

      const ldownloadTxtBtn = document.getElementById('ldownloadTxtBtn');

      const ldownloadSrtBtn = document.getElementById('ldownloadSrtBtn');

      const ldownloadEngSrtBtn = document.getElementById('ldownloadEngSrtBtn');

      const downloadTxtBtn = document.getElementById('downloadTxtBtn');

      const downloadSrtBtn = document.getElementById('downloadSrtBtn');

      const uploadStatus = document.getElementById('uploadStatus');

      const uploadBtnDiv = document.getElementsByClassName('uploadBtnDiv');

      const loginBtn = document.getElementById('loginBtn');

      const fileInput = document.querySelector('#audio-file');

      const fileLabel = document.querySelector('#file-label span:first-of-type');

      const resetButton = document.querySelector('#resetButton');

      const sendMail = document.querySelector('#sendMail');

      const messageDialog = document.querySelector('#message_dialog_modal');

      const backmessageDialog = document.querySelector('#back_message_dialog_modal');

      var fsize="";

window.onload = function () 

      {

        let textAreaData = localStorage.getItem("textareaData");

        if(textAreaData.trim()===""){

          //window.location.reload();

          try {

            ldownloadTxtBtn.style.display="none";

            ldownloadSrtBtn.style.display="none";

            ldownloadEngSrtBtn.style.display="none";

            resetButton.style.display="none";

            sendMail.style.display="none";

          } catch (error) {

            

          }

        }else{

          document.getElementById("card-textarea").innerHTML = textAreaData;

          localStorage.removeItem("textareaData");

          try {

            ldownloadTxtBtn.style.display="inline-block";

            ldownloadSrtBtn.style.display="inline-block";

            ldownloadEngSrtBtn.style.display="inline-block";

            resetButton.style.display="inline-block";

            sendMail.style.display="inline-block";

          } catch (error) {

            

          }

        }

      }



      

      fileInput.addEventListener('change', () => {

        fileLabel.textContent = fileInput.files[0].name;

        fsize=fileInput.files[0].size;

        console.log(fsize);

      });

      try {

        

        

        form.addEventListener('submit', (event) => {

          var files=document.querySelector('#audio-file').files;

          var fiSize = files[0].size;

          console.log("file size: "+ fiSize);

          if(fiSize<2*1024*1024){

            

            event.preventDefault();



            output.style.display = 'inline-block';

            uploadStatus.innerHTML="Uploading..."

            document.getElementById("lottie_modal").classList.remove('hidden');

            const formData = new FormData(form);

            fetch('/process_file', {

              method: 'POST',

              body: formData,

              

            })

            .then(response => response.json())

            .then(data => {

              output.style.display = 'none';

              try {

                

              ldownloadTxtBtn.style.display="inline-block";

              ldownloadSrtBtn.style.display="inline-block";

              ldownloadEngSrtBtn.style.display="inline-block";

              resetButton.style.display="inline-block";

              sendMail.style.display="inline-block";

              } catch (error) {

                console.log(error)

              }

              

              uploadStatus.innerHTML="Upload"

              document.getElementById("lottie_modal").classList.add('hidden');

              textarea.innerHTML = data.text; 
              document.getElementById('copy').style.display = 'inline-block';

            })

            .catch(error => {

              uploadStatus.innerHTML="Upload"

              console.error(error);

              output.innerHTML = 'Something Went wrong! Reload the Page';

              document.getElementById("lottie_modal").classList.add('hidden');

            });

        }

          else{

            event.preventDefault();

            DayPilot.Modal.confirm("File is seems to be big!\n Do you want to send as email or wait?",{theme:"modal_rounded", okText: "Sent via mail", cancelText: "I'll wait"})

            .then(function(args) {

            if (args.result) {

              event.preventDefault();

              document.getElementById("back_message_dialog_modal").classList.remove('hidden');

              

              const formData = new FormData(form);

              fetch('/send-as-mail-background', {

                method: 'POST',

                body: formData,

                

                

              })

              .then(response => response.json())

              .then(data => {

                

              })

              .catch(error => {

                

              });

            }

            else {

              event.preventDefault();



              output.style.display = 'inline-block';

              uploadStatus.innerHTML="Uploading..."

              document.getElementById("lottie_modal").classList.remove('hidden');

              const formData = new FormData(form);

              fetch('/process_file', {

                method: 'POST',

                body: formData,

                

              })

              .then(response => response.json())

              .then(data => {

                output.style.display = 'none';

                try {

                  

                ldownloadTxtBtn.style.display="inline-block";

                ldownloadSrtBtn.style.display="inline-block";

                ldownloadEngSrtBtn.style.display="inline-block";

                resetButton.style.display="inline-block";

                sendMail.style.display="inline-block";

                } catch (error) {

                  console.log(error)

                }

                

                uploadStatus.innerHTML="Upload"

                document.getElementById("lottie_modal").classList.add('hidden');

                textarea.innerHTML = data.text; 

              })

              .catch(error => {

                uploadStatus.innerHTML="Upload"

                console.error(error);

                output.innerHTML = 'Something Went wrong! Reload the Page';

                document.getElementById("lottie_modal").classList.add('hidden');

              });

          }

        });

            /*if (confirm("Do you want to send as email or wait?")) {

              // If user clicks "OK", send as email

              event.preventDefault();

              document.getElementById("send_email_model").classList.remove('hidden');

              

              const formData = new FormData(form);

              fetch('/send-as-mail-background', {

                method: 'POST',

                body: formData,

                

                

              })

              .then(response => response.json())

              .then(data => {

                

              })

              .catch(error => {

                

              });

            } else {

              // If user clicks "Cancel", wait

              event.preventDefault();



            output.style.display = 'inline-block';

            uploadStatus.innerHTML="Uploading..."

            document.getElementById("lottie_modal").classList.remove('hidden');

            const formData = new FormData(form);

            fetch('/process_file', {

              method: 'POST',

              body: formData,

              

            })

            .then(response => response.json())

            .then(data => {

              output.style.display = 'none';

              try {

                

              ldownloadTxtBtn.style.display="inline-block";

              ldownloadSrtBtn.style.display="inline-block";

              ldownloadEngSrtBtn.style.display="inline-block";

              resetButton.style.display="inline-block";

              sendMail.style.display="inline-block";

              } catch (error) {

                console.log(error)

              }

              

              uploadStatus.innerHTML="Upload"

              document.getElementById("lottie_modal").classList.add('hidden');

              textarea.innerHTML = data.text; 

            })

            .catch(error => {

              uploadStatus.innerHTML="Upload"

              console.error(error);

              output.innerHTML = 'Something Went wrong! Reload the Page';

              document.getElementById("lottie_modal").classList.add('hidden');

            });

            }*/

              

            

          }

        });



      }

      

        

      catch (error) {

        console.log(error);

      }

      

      startRecordButton.addEventListener('click',() => {

        window.location.href="/live"

});

function openModal() {

  document.getElementById('modal').classList.remove('hidden');

  let textAreaData = document.getElementById("card-textarea").value;

  localStorage.setItem("textareaData", textAreaData);



}
function copy() {

  navigator.clipboard.writeText(textarea.value);
}

function openMessageDialog(){

  document.getElementById('send_email_model').classList.add('hidden');

  document.getElementById('back_message_dialog_modal').classList.remove('hidden');

}



function closeModal() {

  document.getElementById('modal').classList.add('hidden');

}

try{

function closeMessageModal() {

  location.href="/";

}

}catch (error) {

  console.log(error)

}





function copyToClipboard() {



  navigator.clipboard.writeText(textarea.value);

}



textarea.addEventListener("contextmenu", function(event) {

  event.preventDefault();

});

fileInput.addEventListener('change', function(event) {

  if(fileInput.value){

    

    var fileSize = fileInput.files[0].size;

    console.log(fileSize);

    if (fileSize > 2 * 1024 * 1024) {

  //document.getElementById("send_email_model").classList.remove("hidden");

  uploadStatus.style.display='inline-block';

  uploadStatus.style.justifyContent='center';

 // document.getElementById("fileSize").innerHTML = "";

}

else{

  uploadStatus.style.display='inline-block';

  uploadStatus.style.justifyContent='center';

 // document.getElementById("send_email_model").classList.add("hidden");

}

  }

  else{

    uploadStatus.style.display='none';

  }

});

 

function autoSize(textarea) {

  textarea.style.height='auto';

  textarea.style.height='${textarea.scrollHeight}px';





}

function resetTextField() {

  location.reload();

  



}

