document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.carousel__container');
  const cells = document.querySelectorAll('.carousel__cell');
  const totalCells = cells.length;
  const angle = 360 / totalCells; // Calcula el ángulo para cada imagen
  let currentRotation = 0; // Rotación actual del carrusel

  // Posiciona las imágenes en el carrusel
  const positionCells = () => {
    cells.forEach((cell, i) => {
      const rotation = angle * i;
      cell.style.transform = `rotateY(${rotation}deg) translateZ(300px)`; // Posiciona las imágenes en círculo
    });
  };

  // Rota el carrusel continuamente
  const rotateCarousel = () => {
    currentRotation -= 0.1; // Ajusta la velocidad de rotación (más lento o más rápido)
    container.style.transform = `rotateY(${currentRotation}deg)`;
    requestAnimationFrame(rotateCarousel); // Llama a la función en el siguiente frame
  };

  // Inicializa el carrusel
  positionCells();
  rotateCarousel();
});