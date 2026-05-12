// OSQAr figure zoom — makes figures in .gsn-figure containers
// clickable to open full-size in a new tab.
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.gsn-figure img').forEach(function(img) {
    img.style.cursor = 'zoom-in';
    img.title = 'Click to open full size in new tab';
    img.addEventListener('click', function(e) {
      var link = img.closest('a');
      window.open(link ? link.href : img.src, '_blank');
      e.preventDefault();
    });
  });
});
