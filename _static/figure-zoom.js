// OSQAr figure zoom — click any .gsn-figure container to open
// a full-viewport lightbox for detailed examination.
//
// PlantUML renders <object> elements which create nested browsing
// contexts — clicks on the embedded SVG never bubble to the parent
// document.  We work around this by placing a transparent click
// layer on top of <object>-backed figures.
(function() {
  'use strict';

  function findBestSrc(container) {
    // PlantUML: <object data="...svg"><img src="...png"></object>
    var obj = container.querySelector('object[data]');
    if (obj) return obj.getAttribute('data');

    // Regular image (gsn2x SVG, PNG screenshots, etc.)
    var img = container.querySelector('img[src]');
    if (img) return img.getAttribute('src');

    // Wrapped in <a href="...">
    var link = container.querySelector('a[href]');
    if (link) return link.getAttribute('href');

    return null;
  }

  function showLightbox(src) {
    var existing = document.getElementById('osqar-lightbox');
    if (existing) existing.remove();

    var overlay = document.createElement('div');
    overlay.id = 'osqar-lightbox';
    overlay.innerHTML =
      '<div class="osqar-lightbox-close">&times;</div>' +
      '<img src="' + src + '" alt="Full-size diagram" />';

    overlay.addEventListener('click', function(e) {
      if (e.target === overlay || e.target.classList.contains('osqar-lightbox-close')) {
        overlay.remove();
      }
    });

    document.addEventListener('keydown', function escHandler(e) {
      if (e.key === 'Escape') {
        overlay.remove();
        document.removeEventListener('keydown', escHandler);
      }
    });

    document.body.appendChild(overlay);
  }

  function onFigureClick(container, e) {
    if (e.target.classList.contains('headerlink')) return;
    var src = findBestSrc(container);
    if (src) showLightbox(src);
  }

  function init() {
    document.querySelectorAll('.gsn-figure').forEach(function(container) {
      var hasObject = container.querySelector('object[data]');

      if (hasObject) {
        // PlantUML: <object> blocks click bubbling — place a
        // transparent layer on top to capture clicks.
        container.style.position = 'relative';
        var clickLayer = document.createElement('div');
        clickLayer.className = 'gsn-figure-click-layer';
        clickLayer.style.cssText =
          'position:absolute;top:0;left:0;width:100%;height:100%;' +
          'z-index:1;cursor:zoom-in';
        clickLayer.title = 'Click for detailed view';
        clickLayer.addEventListener('click', function(e) {
          onFigureClick(container, e);
          e.stopPropagation();
        });
        container.appendChild(clickLayer);
      } else {
        // gsn2x SVG / PNG: clicks bubble normally to the container
        var img = container.querySelector('img');
        if (img) {
          img.style.cursor = 'zoom-in';
          img.title = 'Click for detailed view';
        }
        container.style.cursor = 'pointer';
        container.addEventListener('click', function(e) {
          onFigureClick(container, e);
        });
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
