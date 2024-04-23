document.addEventListener('DOMContentLoaded', function() {
  var sendMessageButton = document.getElementById("sendMessageButton");
  var chatInput = document.getElementById("chatInput");
  var chatOutput = document.getElementById("chatOutput");
  var imageOutput = document.getElementById("imageOutput");

  if (sendMessageButton && chatInput) {
    sendMessageButton.addEventListener("click", sendMessage);
    chatInput.addEventListener("keyup", function(event) {
      if (event.keyCode === 13) {  // Enter key
        sendMessage();
      }
    });
  }

  function sendMessage() {
    var userInput = chatInput.value.trim();
    if (userInput === "") return;  // Don't send empty messages

    chatOutput.innerHTML += `<div class="user-message">Du: ${userInput}</div>`;
    chatInput.value = '';  // Clear the input box after sending the message

    fetch('/ask_pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_question: userInput })
    })
    .then(response => response.json())
    .then(data => {
      chatOutput.innerHTML += `<div class="gpt-message">Nova: ${data.answer || 'No response from server'}</div>`;
      displayImages(data.images);
      chatOutput.scrollTop = chatOutput.scrollHeight;  // Scroll to the bottom of the chat window
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  function displayImages(images) {
    imageOutput.innerHTML = '';  // Clear previous images
    if (images && images.length > 0) {
      images.forEach(function(base64String) {
        var img = new Image();
        img.src = 'data:image/jpeg;base64,' + base64String;
        img.className = 'response-image';
        imageOutput.appendChild(img);
      });
    }
  }
});
