document.addEventListener('DOMContentLoaded', function() {
  var sendMessageButton = document.getElementById("sendMessageButton");
  var chatInput = document.getElementById("chatInput");
  var chatOutput = document.getElementById("chatOutput");
  var imageOutput = document.getElementById("imageOutput");

  if (sendMessageButton && chatInput) {
    sendMessageButton.addEventListener("click", sendMessage);
    chatInput.addEventListener("keyup", function(event) {
      // Number 13 is the "Enter" key on the keyboard
      if (event.keyCode === 13) {
        sendMessage();
      }
    });
  }

  function sendMessage() {
    var userInput = chatInput.value;
    if (userInput.trim() === "") return; // Don't send empty messages

    // Display the user's question in the chat window
    chatOutput.innerHTML += `<div class="user-message">Du: ${userInput}</div>`;

    // Send the user's question to the server
    fetch('/ask_pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_question: userInput })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Received data from server:", data); // Debugging log

      // Display GPT's answer in the chat window
      chatOutput.innerHTML += `<div class="gpt-message">Nova: ${data.answer || 'No response from server'}</div>`;

      // Handle image display
      imageOutput.innerHTML = ''; // Clear previous images
      if (data.images && data.images.length > 0) {
        console.log("Attempting to display images:", data.images.length); // Debugging log
        data.images.forEach(function(base64String) {
          console.log("Image Base64 Length:", base64String.length); // Debugging log for image data length
          var img = new Image();
          img.src = 'data:image/jpeg;base64,' + base64String;
          img.className = 'response-image';
          imageOutput.appendChild(img);
        });
      }

      // Scroll to the bottom of the chat window
      chatOutput.scrollTop = chatOutput.scrollHeight;
    })
    .catch(error => {
      console.error('Error:', error);
    });

    // Clear the input box after sending the message
    chatInput.value = '';
  }
});
