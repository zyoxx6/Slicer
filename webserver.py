from flask import Flask
from threading import Thread


app = Flask('')

html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Bot Status</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');
    body {
      background: linear-gradient(135deg, #1e3c72, #2a5298);
      height: 100vh;
      margin: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      font-family: 'Poppins', sans-serif;
      color: #fff;
      overflow: hidden;
    }
    .container {
      text-align: center;
      animation: fadeIn 2s ease forwards;
    }
    h1 {
      font-size: 3rem;
      margin-bottom: 1rem;
      letter-spacing: 2px;
      animation: glow 3s ease-in-out infinite alternate;
    }
    p {
      font-size: 1.25rem;
      opacity: 0.8;
      animation: slideUp 1.5s ease forwards;
    }

    /* Animations */
    @keyframes glow {
      from {
        text-shadow: 0 0 10px #00ffe7, 0 0 20px #00ffe7, 0 0 30px #00ffe7;
        color: #00fff7;
      }
      to {
        text-shadow: 0 0 20px #ff007c, 0 0 30px #ff007c, 0 0 40px #ff007c;
        color: #ff2a6d;
      }
    }
    @keyframes fadeIn {
      from {opacity: 0; transform: translateY(20px);}
      to {opacity: 1; transform: translateY(0);}
    }
    @keyframes slideUp {
      from {opacity: 0; transform: translateY(30px);}
      to {opacity: 0.8; transform: translateY(0);}
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🤖 Bot is Alive!</h1>
    <p>Keepin’ it 100, 24/7 online and vibin’</p>
  </div>
</body>
</html>
"""

@app.route("/")
def home():
    return html

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
