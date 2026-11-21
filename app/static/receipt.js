document.addEventListener('DOMContentLoaded', () => {
  const receipt = document.getElementById('receipt');
  const png = document.getElementById('download-png');
  const pdf = document.getElementById('download-pdf');
  if (!receipt) return;
  png?.addEventListener('click', async () => {
    if (!window.html2canvas) return alert('No se pudo cargar el generador de imágenes. Revisa tu conexión e inténtalo de nuevo.');
    const canvas = await window.html2canvas(receipt, {backgroundColor: '#f6f2ef', scale: 2});
    const link = document.createElement('a');
    link.download = 'beagle-games-comprobante.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  });
  pdf?.addEventListener('click', () => {
    if (!window.html2pdf) return alert('No se pudo cargar el generador de PDF. Revisa tu conexión e inténtalo de nuevo.');
    window.html2pdf().set({margin: 10, filename: 'beagle-games-comprobante.pdf', image: {type: 'jpeg', quality: 0.98}, html2canvas: {scale: 2}, jsPDF: {unit: 'mm', format: 'a4', orientation: 'portrait'}}).from(receipt).save();
  });
});
