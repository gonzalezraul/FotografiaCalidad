document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.carousel__container');
  const cells = document.querySelectorAll('.carousel__cell');
  const totalCells = cells.length;
  const angle = 360 / totalCells; // Ángulo para cada imagen
  let currentRotation = 0; // Rotación actual del carrusel

  // Posicionar las imágenes en el carrusel con mayor profundidad
  const positionCells = () => {
    cells.forEach((cell, i) => {
      const rotation = angle * i;
      cell.style.transform = `rotateY(${rotation}deg) translateZ(400px)`;
    });
  };

  const rotateCarousel = () => {
    currentRotation -= 0.1;
    container.style.transform = `rotateY(${currentRotation}deg)`;
    requestAnimationFrame(rotateCarousel);
  };

  positionCells();
  rotateCarousel();
});