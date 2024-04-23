document.addEventListener('DOMContentLoaded', function() {
  var sendMessageButton = document.getElementById("sendMessageButton");
  var chatInput = document.getElementById("chatInput");

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
    var chatOutput = document.getElementById("chatOutput");
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
      // Display GPT's answer in the chat window
      chatOutput.innerHTML += `<div class="gpt-message">Nova: ${data.answer || data.error}</div>`;
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
