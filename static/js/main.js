// Initialize 3D background
function init3DBackground() {
    const container = document.getElementById('canvas-container');
    
    // Create scene
    const scene = new THREE.Scene();
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 30;
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Create floating airplanes
    const airplaneGeometry = new THREE.ConeGeometry(0.5, 2, 4);
    airplaneGeometry.rotateX(Math.PI / 2);
    
    const airplanes = [];
    const colors = [0x3498db, 0xe74c3c, 0x2ecc71, 0xf1c40f, 0x9b59b6];
    
    for (let i = 0; i < 15; i++) {
        const color = colors[Math.floor(Math.random() * colors.length)];
        const material = new THREE.MeshPhongMaterial({ color });
        const airplane = new THREE.Mesh(airplaneGeometry, material);
        
        // Random position
        airplane.position.x = (Math.random() - 0.5) * 50;
        airplane.position.y = (Math.random() - 0.5) * 30;
        airplane.position.z = (Math.random() - 0.5) * 50;
        
        // Random rotation
        airplane.rotation.z = Math.random() * Math.PI * 2;
        
        // Random speed
        airplane.userData = {
            speed: 0.01 + Math.random() * 0.02,
            rotationSpeed: (Math.random() - 0.5) * 0.01
        };
        
        scene.add(airplane);
        airplanes.push(airplane);
    }
    
    // Add stars
    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.1 });
    
    const starVertices = [];
    for (let i = 0; i < 1000; i++) {
        starVertices.push(
            (Math.random() - 0.5) * 2000,
            (Math.random() - 0.5) * 2000,
            (Math.random() - 0.5) * 2000
        );
    }
    
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        // Animate airplanes
        airplanes.forEach(airplane => {
            airplane.position.z -= airplane.userData.speed;
            airplane.rotation.z += airplane.userData.rotationSpeed;
            
            // Reset position if out of view
            if (airplane.position.z < -50) {
                airplane.position.z = 50;
                airplane.position.x = (Math.random() - 0.5) * 50;
                airplane.position.y = (Math.random() - 0.5) * 30;
            }
        });
        
        renderer.render(scene, camera);
    }
    
    // Handle window resize
    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    window.addEventListener('resize', onWindowResize, false);
    
    // Start animation
    animate();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    init3DBackground();
    
    // Add animation to cards on scroll
    const animateOnScroll = function() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            const cardPosition = card.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (cardPosition < screenPosition) {
                card.classList.add('animate__animated', 'animate__fadeInUp');
            }
        });
    };
    
    window.addEventListener('scroll', animateOnScroll);
    
    // Initialize socket.io
    const socket = io();
    
    // Handle real-time updates
    socket.on('data_update', function(data) {
        // You could show a notification when new data is available
        console.log('New data available:', data);
    });
});