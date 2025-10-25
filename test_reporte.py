<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar Sesión</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="icon" type="image/png" href="static/img/icon.png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e2836 0%, #2c3e50 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .login-container {
            display: flex;
            max-width: 1100px;
            width: 100%;
            background: #2c3845;
            border-radius: 25px;
            overflow: hidden;
            box-shadow: 0 25px 70px rgba(0, 0, 0, 0.6);
        }

        .login-form-section {
            flex: 1;
            padding: 60px 50px;
            background: #2c3845;
        }

        .welcome-header {
            margin-bottom: 40px;
        }

        .welcome-header i {
            font-size: 45px;
            color: #17a2b8;
            margin-bottom: 15px;
        }

        .welcome-header h1 {
            color: #17a2b8;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .welcome-header p {
            color: #a0aab8;
            font-size: 17px;
        }

        .form-group {
            margin-bottom: 28px;
        }

        .form-group label {
            display: block;
            color: #17a2b8;
            font-size: 15px;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .input-wrapper {
            position: relative;
        }

        .input-wrapper i {
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: #17a2b8;
            font-size: 18px;
        }

        .form-control {
            width: 100%;
            padding: 16px 18px 16px 50px;
            background: #3d4f61;
            border: 2px solid transparent;
            border-radius: 12px;
            color: #fff;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: #17a2b8;
            background: #344150;
            box-shadow: 0 0 0 4px rgba(23, 162, 184, 0.1);
        }

        .form-control::placeholder {
            color: #7a8a9b;
        }

        .btn-login {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 15px;
        }

        .btn-login:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(23, 162, 184, 0.5);
        }

        .btn-login i {
            margin-right: 10px;
        }

        .footer-text {
            text-align: center;
            margin-top: 35px;
            color: #8b96a5;
            font-size: 14px;
        }

        .footer-text i {
            margin-right: 6px;
            color: #17a2b8;
        }

        .illustration-section {
            flex: 1.2;
            background: linear-gradient(135deg, #17a2b8 0%, #0e7c8c 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 50px;
            position: relative;
            overflow: hidden;
        }

        .illustration-section::before {
            content: '';
            position: absolute;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
            border-radius: 50%;
            top: -150px;
            right: -150px;
            animation: pulse-slow 4s ease-in-out infinite;
        }

        .illustration-section::after {
            content: '';
            position: absolute;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
            border-radius: 50%;
            bottom: -100px;
            left: -100px;
            animation: pulse-slow 5s ease-in-out infinite reverse;
        }

        @keyframes pulse-slow {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }

        .illustration-content {
            text-align: center;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .paper-container {
            position: relative;
            margin-bottom: 40px;
            animation: float 4s ease-in-out infinite;
            filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.4));
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(-2deg); }
            50% { transform: translateY(-20px) rotate(2deg); }
        }

        .paper {
            width: 240px;
            height: 320px;
            background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 15px;
            position: relative;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 20px;
        }

        .paper::before {
            content: '';
            position: absolute;
            top: 25px;
            left: 25px;
            right: 25px;
            height: 3px;
            background: linear-gradient(90deg, #17a2b8 0%, transparent 100%);
            border-radius: 2px;
        }

        .paper-lines {
            position: absolute;
            top: 50px;
            left: 25px;
            right: 25px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .paper-line {
            height: 2px;
            background: linear-gradient(90deg, #dee2e6 0%, #f1f3f5 100%);
            border-radius: 1px;
        }

        .paper-face {
            position: relative;
            margin-top: 120px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }

        .blush {
            position: absolute;
            width: 20px;
            height: 15px;
            background: #ffb3ba;
            border-radius: 50%;
            opacity: 0.6;
            top: 15px;
        }

        .blush.left {
            left: -45px;
        }

        .blush.right {
            right: -45px;
        }

        .eyes-container {
            display: flex;
            gap: 45px;
            justify-content: center;
            position: relative;
            margin-bottom: 15px;
        }

        .eye {
            width: 32px;
            height: 32px;
            background: white;
            border: 4px solid #2c3845;
            border-radius: 50%;
            position: relative;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .pupil {
            width: 14px;
            height: 14px;
            background: #2c3845;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            transition: all 0.3s ease;
        }

        .pupil::after {
            content: '';
            width: 5px;
            height: 5px;
            background: white;
            border-radius: 50%;
            position: absolute;
            top: 3px;
            left: 3px;
        }

        .sparkle {
            position: absolute;
            color: #ffd700;
            font-size: 12px;
            animation: sparkle 1.5s ease-in-out infinite;
        }

        .sparkle-1 { top: -20px; left: -20px; animation-delay: 0s; }
        .sparkle-2 { top: -15px; right: -20px; animation-delay: 0.5s; }
        .sparkle-3 { bottom: -15px; left: -15px; animation-delay: 1s; }

        @keyframes sparkle {
            0%, 100% { opacity: 0; transform: scale(0); }
            50% { opacity: 1; transform: scale(1); }
        }

        .hands {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 30px;
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            z-index: 10;
        }

        .hands.covering {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        .hand {
            width: 38px;
            height: 42px;
            background: linear-gradient(145deg, #ffd1a3 0%, #ffb380 100%);
            border-radius: 18px 18px 10px 10px;
            position: relative;
            border: 3px solid #e6b88a;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .hand::before,
        .hand::after {
            content: '';
            position: absolute;
            background: linear-gradient(145deg, #ffd1a3 0%, #ffb380 100%);
            border: 2px solid #e6b88a;
            border-radius: 50%;
        }

        .hand::before {
            width: 10px;
            height: 12px;
            top: -4px;
            left: -6px;
        }

        .hand::after {
            width: 10px;
            height: 12px;
            top: -4px;
            right: -6px;
        }

        .mouth {
            width: 35px;
            height: 18px;
            border: 4px solid #2c3845;
            border-top: none;
            border-radius: 0 0 18px 18px;
            margin-top: 8px;
            transition: all 0.3s ease;
        }

        .mouth.surprised {
            width: 25px;
            height: 25px;
            border: 4px solid #2c3845;
            border-radius: 50%;
            background: white;
        }

        .brand-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }

        .brand-name {
            font-size: 52px;
            font-weight: 800;
            color: white;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
            letter-spacing: 2px;
        }

        .fingerprint-icon {
            font-size: 70px;
            color: rgba(255, 255, 255, 0.95);
            animation: pulse-fingerprint 2.5s ease-in-out infinite;
        }

        @keyframes pulse-fingerprint {
            0%, 100% { 
                opacity: 0.8; 
                transform: scale(1);
                filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
            }
            50% { 
                opacity: 1; 
                transform: scale(1.15);
                filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.8));
            }
        }

        .security-badges {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 25px;
            flex-wrap: wrap;
        }

        .badge {
            background: rgba(255, 255, 255, 0.25);
            padding: 12px 24px;
            border-radius: 30px;
            color: white;
            font-size: 15px;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .badge i {
            margin-right: 8px;
        }

        .copyright {
            position: absolute;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            text-align: center;
            width: 90%;
            font-weight: 500;
        }

        @media (max-width: 768px) {
            .login-container {
                flex-direction: column;
            }

            .illustration-section {
                padding: 40px;
            }

            .login-form-section {
                padding: 40px 30px;
            }

            .paper {
                width: 200px;
                height: 270px;
            }

            .brand-name {
                font-size: 38px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-form-section">
            <div class="welcome-header">
                <i class="fas fa-fingerprint"></i>
                <h1>Bienvenido</h1>
                <p>Portal de asistencia biométrica</p>
            </div>

            <form method="POST">
                <div class="form-group">
                    <label for="username">Usuario</label>
                    <div class="input-wrapper">
                        <i class="fas fa-user"></i>
                        <input type="text" class="form-control" id="username" name="username" 
                               placeholder="Ingrese su usuario" required>
                    </div>
                </div>

                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <div class="input-wrapper">
                        <i class="fas fa-lock"></i>
                        <input type="password" class="form-control" id="password" name="password" 
                               placeholder="Ingrese su contraseña" required>
                    </div>
                </div>

                <button type="submit" class="btn-login">
                    <i class="fas fa-sign-in-alt"></i>Iniciar sesión
                </button>
            </form>

            <div class="footer-text">
                <i class="fas fa-shield-alt"></i>
                Acceso restringido para administradores
            </div>
        </div>

        <div class="illustration-section">
            <div class="illustration-content">
                <div class="paper-container">
                    <div class="sparkle sparkle-1">✨</div>
                    <div class="sparkle sparkle-2">✨</div>
                    <div class="sparkle sparkle-3">✨</div>
                    <div class="paper">
                        <div class="paper-lines">
                            <div class="paper-line"></div>
                            <div class="paper-line"></div>
                            <div class="paper-line"></div>
                            <div class="paper-line"></div>
                            <div class="paper-line"></div>
                            <div class="paper-line"></div>
                            <div class="paper-line"></div>
                        </div>
                        <div class="paper-face">
                            <div class="blush left"></div>
                            <div class="blush right"></div>
                            <div class="eyes-container">
                                <div class="eye">
                                    <div class="pupil"></div>
                                </div>
                                <div class="eye">
                                    <div class="pupil"></div>
                                </div>
                                <div class="hands" id="hands">
                                    <div class="hand"></div>
                                    <div class="hand"></div>
                                </div>
                            </div>
                            <div class="mouth" id="mouth"></div>
                        </div>
                    </div>
                </div>
                
            
            </div>
            <div class="copyright">
                 © 2025 VeliorSoft — Sistema QR
            </div>
        </div>
    </div>

    <script>
        const passwordInput = document.getElementById('password');
        const hands = document.getElementById('hands');
        const mouth = document.getElementById('mouth');

        passwordInput.addEventListener('focus', () => {
            hands.classList.add('covering');
            mouth.classList.add('surprised');
        });

        passwordInput.addEventListener('blur', () => {
            if (passwordInput.value.length === 0) {
                hands.classList.remove('covering');
                mouth.classList.remove('surprised');
            }
        });

        passwordInput.addEventListener('input', () => {
            if (passwordInput.value.length > 0) {
                hands.classList.add('covering');
                mouth.classList.add('surprised');
            }
        });
    </script>
</body>
</html>