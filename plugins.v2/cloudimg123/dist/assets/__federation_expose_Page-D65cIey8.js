import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

function formatFileSize(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}
function formatDateTime(dateString) {
  try {
    const date = new Date(dateString);
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  } catch {
    return dateString;
  }
}
function formatTimeAgo(dateString) {
  try {
    const date = new Date(dateString);
    const now = /* @__PURE__ */ new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1e3 * 60));
    const diffHours = Math.floor(diffMs / (1e3 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1e3 * 60 * 60 * 24));
    if (diffMinutes < 1) {
      return "刚刚";
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分钟前`;
    } else if (diffHours < 24) {
      return `${diffHours}小时前`;
    } else if (diffDays < 30) {
      return `${diffDays}天前`;
    } else {
      return date.toLocaleDateString("zh-CN");
    }
  } catch {
    return dateString;
  }
}
async function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      console.log("已成功复制到剪贴板 (使用 Navigator Clipboard API)");
      return true;
    } catch (err) {
      console.error("使用 Clipboard API 复制失败:", err);
      return fallbackCopyToClipboard(text);
    }
  } else {
    console.warn("Clipboard API 不可用，使用备用方法回退。");
    return fallbackCopyToClipboard(text);
  }
}
function fallbackCopyToClipboard(text) {
  console.log("备用方法正在尝试复制以下文本:", `"${text}"`);
  if (!text) {
    console.error("备用方法接收到空文本，复制已取消。");
    return false;
  }
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.top = "0";
  textArea.style.left = "0";
  textArea.style.width = "2em";
  textArea.style.height = "2em";
  textArea.style.padding = "0";
  textArea.style.border = "none";
  textArea.style.outline = "none";
  textArea.style.boxShadow = "none";
  textArea.style.background = "transparent";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  let success = false;
  try {
    success = document.execCommand("copy");
    if (success) {
      console.log("备用方法: document.execCommand 返回 true (可能成功)");
    } else {
      console.error("备用方法: document.execCommand 明确返回 false");
    }
  } catch (err) {
    console.error("执行备用复制方法时抛出错误:", err);
    success = false;
  }
  document.body.removeChild(textArea);
  return success;
}
function validateImageFile(file) {
  const supportedTypes = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/tiff",
    "image/ico",
    "image/svg+xml"
  ];
  if (!supportedTypes.includes(file.type)) {
    return { valid: false, message: "不支持的文件格式，仅支持图片文件" };
  }
  const maxSize = 100 * 1024 * 1024;
  if (file.size > maxSize) {
    return { valid: false, message: "文件过大，最大支持100MB" };
  }
  if (file.size === 0) {
    return { valid: false, message: "文件为空" };
  }
  return { valid: true };
}

const useImageLazyLoad = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      console.log("[懒加载调试] IntersectionObserver 检测到图片:", {
        isIntersecting: entry.isIntersecting,
        fileId: entry.target.dataset.fileId,
        src: entry.target.src,
        dataSrc: entry.target.dataset.src
      });
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.dataset.src;
        const lazyType = img.dataset.lazyType;
        const fileId = img.dataset.fileId;
        if (src) {
          if (lazyType === "thumbnail" && fileId) {
            console.log("[懒加载调试] 图片进入视口，触发缩略图事件:", { fileId, img });
            const event = new CustomEvent("lazy-load-thumbnail", {
              detail: { img, fileId },
              bubbles: true
            });
            document.dispatchEvent(event);
          } else {
            img.src = src;
            img.removeAttribute("data-src");
            img.onload = () => {
              img.classList.add("lazy-loaded");
              observer.unobserve(img);
            };
            img.onerror = () => {
              observer.unobserve(img);
              img.classList.add("lazy-error");
              img.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0zNSA0MEw0NSAzMEw2NSA1MEw4MCAzNUw5NSA1MEw5NSA4MEg1VjcwTDMwIDU1TDM1IDQwWiIgZmlsbD0iI0Q5RDlEOSIvPgo8Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSI2IiBmaWxsPSIjRDlEOUQ5Ii8+Cjx0ZXh0IHg9IjUwIiB5PSI1NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzk5OTk5OSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEwIj7nlJ/mtLvotb/kuIrkuIDopoHkuI3lm77niYc8L3RleHQ+Cjwvc3ZnPg==";
            };
          }
        }
      }
    });
  }, {
    rootMargin: "100px",
    // 提前100px开始加载
    threshold: 0.1
  });
  const observeImage = (img) => {
    if (img && img.dataset.src && !img.dataset.lazyObserved) {
      observer.observe(img);
      img.dataset.lazyObserved = "true";
    }
  };
  const unobserveImage = (img) => {
    if (img) {
      observer.unobserve(img);
    }
  };
  const destroy = () => {
    observer.disconnect();
  };
  return {
    observeImage,
    unobserveImage,
    destroy
  };
};

const {ref: ref$1,computed: computed$1,onMounted: onMounted$1,onUnmounted: onUnmounted$1,nextTick: nextTick$1} = await importShared('vue');
const useVirtualGrid = (items, itemWidth = 280, itemHeight = 300, gap = 20, containerWidth = 1200) => {
  const scrollTop = ref$1(0);
  const containerRef = ref$1(null);
  const itemsPerRow = computed$1(() => {
    if (!containerRef.value) return 3;
    const availableWidth = containerRef.value.clientWidth - gap;
    return Math.max(1, Math.floor(availableWidth / (itemWidth + gap)));
  });
  const totalRows = computed$1(() => Math.ceil(items.value.length / itemsPerRow.value));
  const rowHeight = itemHeight + gap;
  const visibleRows = computed$1(() => {
    if (!containerRef.value) return { start: 0, end: 0 };
    const containerHeight = containerRef.value.clientHeight;
    const startRow = Math.floor(scrollTop.value / rowHeight);
    const endRow = Math.min(
      startRow + Math.ceil(containerHeight / rowHeight) + 2,
      // 额外加载2行作为缓冲
      totalRows.value
    );
    return { start: startRow, end: endRow };
  });
  const visibleItems = computed$1(() => {
    const { start, end } = visibleRows.value;
    const startIndex = start * itemsPerRow.value;
    const endIndex = Math.min((end + 1) * itemsPerRow.value, items.value.length);
    return items.value.slice(startIndex, endIndex).map((item, index) => {
      const actualIndex = startIndex + index;
      const row = Math.floor(actualIndex / itemsPerRow.value);
      const col = actualIndex % itemsPerRow.value;
      return {
        ...item,
        _virtualIndex: actualIndex,
        _virtualRow: row,
        _virtualCol: col,
        _virtualTop: row * rowHeight,
        _virtualLeft: col * (itemWidth + gap)
      };
    });
  });
  const totalHeight = computed$1(() => totalRows.value * rowHeight);
  const containerStyle = computed$1(() => ({
    height: "600px",
    overflowY: "auto",
    position: "relative",
    width: "100%"
  }));
  const contentStyle = computed$1(() => ({
    position: "relative",
    height: `${totalHeight.value}px`,
    width: "100%"
  }));
  const handleScroll = () => {
    if (containerRef.value) {
      scrollTop.value = containerRef.value.scrollTop;
    }
  };
  const scrollToItem = (index) => {
    if (containerRef.value) {
      const row = Math.floor(index / itemsPerRow.value);
      containerRef.value.scrollTop = row * rowHeight;
    }
  };
  const resetScroll = () => {
    if (containerRef.value) {
      containerRef.value.scrollTop = 0;
      scrollTop.value = 0;
    }
  };
  const recalculateLayout = () => {
    nextTick$1(() => {
      if (containerRef.value) {
        scrollTop.value = containerRef.value.scrollTop;
      }
    });
  };
  onMounted$1(() => {
    if (containerRef.value) {
      containerRef.value.addEventListener("scroll", handleScroll);
      window.addEventListener("resize", recalculateLayout);
    }
  });
  onUnmounted$1(() => {
    if (containerRef.value) {
      containerRef.value.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", recalculateLayout);
    }
  });
  return {
    containerRef,
    visibleItems,
    itemsPerRow,
    containerStyle,
    contentStyle,
    scrollToItem,
    resetScroll,
    recalculateLayout
  };
};

function getDefaultExportFromCjs (x) {
	return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, 'default') ? x['default'] : x;
}

var sparkMd5 = {exports: {}};

(function (module, exports) {
	(function (factory) {
	    {
	        // Node/CommonJS
	        module.exports = factory();
	    }
	}(function (undefined$1) {

	    /*
	     * Fastest md5 implementation around (JKM md5).
	     * Credits: Joseph Myers
	     *
	     * @see http://www.myersdaily.org/joseph/javascript/md5-text.html
	     * @see http://jsperf.com/md5-shootout/7
	     */

	    /* this function is much faster,
	      so if possible we use it. Some IEs
	      are the only ones I know of that
	      need the idiotic second function,
	      generated by an if clause.  */
	    var hex_chr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'];

	    function md5cycle(x, k) {
	        var a = x[0],
	            b = x[1],
	            c = x[2],
	            d = x[3];

	        a += (b & c | ~b & d) + k[0] - 680876936 | 0;
	        a  = (a << 7 | a >>> 25) + b | 0;
	        d += (a & b | ~a & c) + k[1] - 389564586 | 0;
	        d  = (d << 12 | d >>> 20) + a | 0;
	        c += (d & a | ~d & b) + k[2] + 606105819 | 0;
	        c  = (c << 17 | c >>> 15) + d | 0;
	        b += (c & d | ~c & a) + k[3] - 1044525330 | 0;
	        b  = (b << 22 | b >>> 10) + c | 0;
	        a += (b & c | ~b & d) + k[4] - 176418897 | 0;
	        a  = (a << 7 | a >>> 25) + b | 0;
	        d += (a & b | ~a & c) + k[5] + 1200080426 | 0;
	        d  = (d << 12 | d >>> 20) + a | 0;
	        c += (d & a | ~d & b) + k[6] - 1473231341 | 0;
	        c  = (c << 17 | c >>> 15) + d | 0;
	        b += (c & d | ~c & a) + k[7] - 45705983 | 0;
	        b  = (b << 22 | b >>> 10) + c | 0;
	        a += (b & c | ~b & d) + k[8] + 1770035416 | 0;
	        a  = (a << 7 | a >>> 25) + b | 0;
	        d += (a & b | ~a & c) + k[9] - 1958414417 | 0;
	        d  = (d << 12 | d >>> 20) + a | 0;
	        c += (d & a | ~d & b) + k[10] - 42063 | 0;
	        c  = (c << 17 | c >>> 15) + d | 0;
	        b += (c & d | ~c & a) + k[11] - 1990404162 | 0;
	        b  = (b << 22 | b >>> 10) + c | 0;
	        a += (b & c | ~b & d) + k[12] + 1804603682 | 0;
	        a  = (a << 7 | a >>> 25) + b | 0;
	        d += (a & b | ~a & c) + k[13] - 40341101 | 0;
	        d  = (d << 12 | d >>> 20) + a | 0;
	        c += (d & a | ~d & b) + k[14] - 1502002290 | 0;
	        c  = (c << 17 | c >>> 15) + d | 0;
	        b += (c & d | ~c & a) + k[15] + 1236535329 | 0;
	        b  = (b << 22 | b >>> 10) + c | 0;

	        a += (b & d | c & ~d) + k[1] - 165796510 | 0;
	        a  = (a << 5 | a >>> 27) + b | 0;
	        d += (a & c | b & ~c) + k[6] - 1069501632 | 0;
	        d  = (d << 9 | d >>> 23) + a | 0;
	        c += (d & b | a & ~b) + k[11] + 643717713 | 0;
	        c  = (c << 14 | c >>> 18) + d | 0;
	        b += (c & a | d & ~a) + k[0] - 373897302 | 0;
	        b  = (b << 20 | b >>> 12) + c | 0;
	        a += (b & d | c & ~d) + k[5] - 701558691 | 0;
	        a  = (a << 5 | a >>> 27) + b | 0;
	        d += (a & c | b & ~c) + k[10] + 38016083 | 0;
	        d  = (d << 9 | d >>> 23) + a | 0;
	        c += (d & b | a & ~b) + k[15] - 660478335 | 0;
	        c  = (c << 14 | c >>> 18) + d | 0;
	        b += (c & a | d & ~a) + k[4] - 405537848 | 0;
	        b  = (b << 20 | b >>> 12) + c | 0;
	        a += (b & d | c & ~d) + k[9] + 568446438 | 0;
	        a  = (a << 5 | a >>> 27) + b | 0;
	        d += (a & c | b & ~c) + k[14] - 1019803690 | 0;
	        d  = (d << 9 | d >>> 23) + a | 0;
	        c += (d & b | a & ~b) + k[3] - 187363961 | 0;
	        c  = (c << 14 | c >>> 18) + d | 0;
	        b += (c & a | d & ~a) + k[8] + 1163531501 | 0;
	        b  = (b << 20 | b >>> 12) + c | 0;
	        a += (b & d | c & ~d) + k[13] - 1444681467 | 0;
	        a  = (a << 5 | a >>> 27) + b | 0;
	        d += (a & c | b & ~c) + k[2] - 51403784 | 0;
	        d  = (d << 9 | d >>> 23) + a | 0;
	        c += (d & b | a & ~b) + k[7] + 1735328473 | 0;
	        c  = (c << 14 | c >>> 18) + d | 0;
	        b += (c & a | d & ~a) + k[12] - 1926607734 | 0;
	        b  = (b << 20 | b >>> 12) + c | 0;

	        a += (b ^ c ^ d) + k[5] - 378558 | 0;
	        a  = (a << 4 | a >>> 28) + b | 0;
	        d += (a ^ b ^ c) + k[8] - 2022574463 | 0;
	        d  = (d << 11 | d >>> 21) + a | 0;
	        c += (d ^ a ^ b) + k[11] + 1839030562 | 0;
	        c  = (c << 16 | c >>> 16) + d | 0;
	        b += (c ^ d ^ a) + k[14] - 35309556 | 0;
	        b  = (b << 23 | b >>> 9) + c | 0;
	        a += (b ^ c ^ d) + k[1] - 1530992060 | 0;
	        a  = (a << 4 | a >>> 28) + b | 0;
	        d += (a ^ b ^ c) + k[4] + 1272893353 | 0;
	        d  = (d << 11 | d >>> 21) + a | 0;
	        c += (d ^ a ^ b) + k[7] - 155497632 | 0;
	        c  = (c << 16 | c >>> 16) + d | 0;
	        b += (c ^ d ^ a) + k[10] - 1094730640 | 0;
	        b  = (b << 23 | b >>> 9) + c | 0;
	        a += (b ^ c ^ d) + k[13] + 681279174 | 0;
	        a  = (a << 4 | a >>> 28) + b | 0;
	        d += (a ^ b ^ c) + k[0] - 358537222 | 0;
	        d  = (d << 11 | d >>> 21) + a | 0;
	        c += (d ^ a ^ b) + k[3] - 722521979 | 0;
	        c  = (c << 16 | c >>> 16) + d | 0;
	        b += (c ^ d ^ a) + k[6] + 76029189 | 0;
	        b  = (b << 23 | b >>> 9) + c | 0;
	        a += (b ^ c ^ d) + k[9] - 640364487 | 0;
	        a  = (a << 4 | a >>> 28) + b | 0;
	        d += (a ^ b ^ c) + k[12] - 421815835 | 0;
	        d  = (d << 11 | d >>> 21) + a | 0;
	        c += (d ^ a ^ b) + k[15] + 530742520 | 0;
	        c  = (c << 16 | c >>> 16) + d | 0;
	        b += (c ^ d ^ a) + k[2] - 995338651 | 0;
	        b  = (b << 23 | b >>> 9) + c | 0;

	        a += (c ^ (b | ~d)) + k[0] - 198630844 | 0;
	        a  = (a << 6 | a >>> 26) + b | 0;
	        d += (b ^ (a | ~c)) + k[7] + 1126891415 | 0;
	        d  = (d << 10 | d >>> 22) + a | 0;
	        c += (a ^ (d | ~b)) + k[14] - 1416354905 | 0;
	        c  = (c << 15 | c >>> 17) + d | 0;
	        b += (d ^ (c | ~a)) + k[5] - 57434055 | 0;
	        b  = (b << 21 |b >>> 11) + c | 0;
	        a += (c ^ (b | ~d)) + k[12] + 1700485571 | 0;
	        a  = (a << 6 | a >>> 26) + b | 0;
	        d += (b ^ (a | ~c)) + k[3] - 1894986606 | 0;
	        d  = (d << 10 | d >>> 22) + a | 0;
	        c += (a ^ (d | ~b)) + k[10] - 1051523 | 0;
	        c  = (c << 15 | c >>> 17) + d | 0;
	        b += (d ^ (c | ~a)) + k[1] - 2054922799 | 0;
	        b  = (b << 21 |b >>> 11) + c | 0;
	        a += (c ^ (b | ~d)) + k[8] + 1873313359 | 0;
	        a  = (a << 6 | a >>> 26) + b | 0;
	        d += (b ^ (a | ~c)) + k[15] - 30611744 | 0;
	        d  = (d << 10 | d >>> 22) + a | 0;
	        c += (a ^ (d | ~b)) + k[6] - 1560198380 | 0;
	        c  = (c << 15 | c >>> 17) + d | 0;
	        b += (d ^ (c | ~a)) + k[13] + 1309151649 | 0;
	        b  = (b << 21 |b >>> 11) + c | 0;
	        a += (c ^ (b | ~d)) + k[4] - 145523070 | 0;
	        a  = (a << 6 | a >>> 26) + b | 0;
	        d += (b ^ (a | ~c)) + k[11] - 1120210379 | 0;
	        d  = (d << 10 | d >>> 22) + a | 0;
	        c += (a ^ (d | ~b)) + k[2] + 718787259 | 0;
	        c  = (c << 15 | c >>> 17) + d | 0;
	        b += (d ^ (c | ~a)) + k[9] - 343485551 | 0;
	        b  = (b << 21 | b >>> 11) + c | 0;

	        x[0] = a + x[0] | 0;
	        x[1] = b + x[1] | 0;
	        x[2] = c + x[2] | 0;
	        x[3] = d + x[3] | 0;
	    }

	    function md5blk(s) {
	        var md5blks = [],
	            i; /* Andy King said do it this way. */

	        for (i = 0; i < 64; i += 4) {
	            md5blks[i >> 2] = s.charCodeAt(i) + (s.charCodeAt(i + 1) << 8) + (s.charCodeAt(i + 2) << 16) + (s.charCodeAt(i + 3) << 24);
	        }
	        return md5blks;
	    }

	    function md5blk_array(a) {
	        var md5blks = [],
	            i; /* Andy King said do it this way. */

	        for (i = 0; i < 64; i += 4) {
	            md5blks[i >> 2] = a[i] + (a[i + 1] << 8) + (a[i + 2] << 16) + (a[i + 3] << 24);
	        }
	        return md5blks;
	    }

	    function md51(s) {
	        var n = s.length,
	            state = [1732584193, -271733879, -1732584194, 271733878],
	            i,
	            length,
	            tail,
	            tmp,
	            lo,
	            hi;

	        for (i = 64; i <= n; i += 64) {
	            md5cycle(state, md5blk(s.substring(i - 64, i)));
	        }
	        s = s.substring(i - 64);
	        length = s.length;
	        tail = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
	        for (i = 0; i < length; i += 1) {
	            tail[i >> 2] |= s.charCodeAt(i) << ((i % 4) << 3);
	        }
	        tail[i >> 2] |= 0x80 << ((i % 4) << 3);
	        if (i > 55) {
	            md5cycle(state, tail);
	            for (i = 0; i < 16; i += 1) {
	                tail[i] = 0;
	            }
	        }

	        // Beware that the final length might not fit in 32 bits so we take care of that
	        tmp = n * 8;
	        tmp = tmp.toString(16).match(/(.*?)(.{0,8})$/);
	        lo = parseInt(tmp[2], 16);
	        hi = parseInt(tmp[1], 16) || 0;

	        tail[14] = lo;
	        tail[15] = hi;

	        md5cycle(state, tail);
	        return state;
	    }

	    function md51_array(a) {
	        var n = a.length,
	            state = [1732584193, -271733879, -1732584194, 271733878],
	            i,
	            length,
	            tail,
	            tmp,
	            lo,
	            hi;

	        for (i = 64; i <= n; i += 64) {
	            md5cycle(state, md5blk_array(a.subarray(i - 64, i)));
	        }

	        // Not sure if it is a bug, however IE10 will always produce a sub array of length 1
	        // containing the last element of the parent array if the sub array specified starts
	        // beyond the length of the parent array - weird.
	        // https://connect.microsoft.com/IE/feedback/details/771452/typed-array-subarray-issue
	        a = (i - 64) < n ? a.subarray(i - 64) : new Uint8Array(0);

	        length = a.length;
	        tail = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
	        for (i = 0; i < length; i += 1) {
	            tail[i >> 2] |= a[i] << ((i % 4) << 3);
	        }

	        tail[i >> 2] |= 0x80 << ((i % 4) << 3);
	        if (i > 55) {
	            md5cycle(state, tail);
	            for (i = 0; i < 16; i += 1) {
	                tail[i] = 0;
	            }
	        }

	        // Beware that the final length might not fit in 32 bits so we take care of that
	        tmp = n * 8;
	        tmp = tmp.toString(16).match(/(.*?)(.{0,8})$/);
	        lo = parseInt(tmp[2], 16);
	        hi = parseInt(tmp[1], 16) || 0;

	        tail[14] = lo;
	        tail[15] = hi;

	        md5cycle(state, tail);

	        return state;
	    }

	    function rhex(n) {
	        var s = '',
	            j;
	        for (j = 0; j < 4; j += 1) {
	            s += hex_chr[(n >> (j * 8 + 4)) & 0x0F] + hex_chr[(n >> (j * 8)) & 0x0F];
	        }
	        return s;
	    }

	    function hex(x) {
	        var i;
	        for (i = 0; i < x.length; i += 1) {
	            x[i] = rhex(x[i]);
	        }
	        return x.join('');
	    }

	    // In some cases the fast add32 function cannot be used..
	    if (hex(md51('hello')) !== '5d41402abc4b2a76b9719d911017c592') ;

	    // ---------------------------------------------------

	    /**
	     * ArrayBuffer slice polyfill.
	     *
	     * @see https://github.com/ttaubert/node-arraybuffer-slice
	     */

	    if (typeof ArrayBuffer !== 'undefined' && !ArrayBuffer.prototype.slice) {
	        (function () {
	            function clamp(val, length) {
	                val = (val | 0) || 0;

	                if (val < 0) {
	                    return Math.max(val + length, 0);
	                }

	                return Math.min(val, length);
	            }

	            ArrayBuffer.prototype.slice = function (from, to) {
	                var length = this.byteLength,
	                    begin = clamp(from, length),
	                    end = length,
	                    num,
	                    target,
	                    targetArray,
	                    sourceArray;

	                if (to !== undefined$1) {
	                    end = clamp(to, length);
	                }

	                if (begin > end) {
	                    return new ArrayBuffer(0);
	                }

	                num = end - begin;
	                target = new ArrayBuffer(num);
	                targetArray = new Uint8Array(target);

	                sourceArray = new Uint8Array(this, begin, num);
	                targetArray.set(sourceArray);

	                return target;
	            };
	        })();
	    }

	    // ---------------------------------------------------

	    /**
	     * Helpers.
	     */

	    function toUtf8(str) {
	        if (/[\u0080-\uFFFF]/.test(str)) {
	            str = unescape(encodeURIComponent(str));
	        }

	        return str;
	    }

	    function utf8Str2ArrayBuffer(str, returnUInt8Array) {
	        var length = str.length,
	           buff = new ArrayBuffer(length),
	           arr = new Uint8Array(buff),
	           i;

	        for (i = 0; i < length; i += 1) {
	            arr[i] = str.charCodeAt(i);
	        }

	        return returnUInt8Array ? arr : buff;
	    }

	    function arrayBuffer2Utf8Str(buff) {
	        return String.fromCharCode.apply(null, new Uint8Array(buff));
	    }

	    function concatenateArrayBuffers(first, second, returnUInt8Array) {
	        var result = new Uint8Array(first.byteLength + second.byteLength);

	        result.set(new Uint8Array(first));
	        result.set(new Uint8Array(second), first.byteLength);

	        return result ;
	    }

	    function hexToBinaryString(hex) {
	        var bytes = [],
	            length = hex.length,
	            x;

	        for (x = 0; x < length - 1; x += 2) {
	            bytes.push(parseInt(hex.substr(x, 2), 16));
	        }

	        return String.fromCharCode.apply(String, bytes);
	    }

	    // ---------------------------------------------------

	    /**
	     * SparkMD5 OOP implementation.
	     *
	     * Use this class to perform an incremental md5, otherwise use the
	     * static methods instead.
	     */

	    function SparkMD5() {
	        // call reset to init the instance
	        this.reset();
	    }

	    /**
	     * Appends a string.
	     * A conversion will be applied if an utf8 string is detected.
	     *
	     * @param {String} str The string to be appended
	     *
	     * @return {SparkMD5} The instance itself
	     */
	    SparkMD5.prototype.append = function (str) {
	        // Converts the string to utf8 bytes if necessary
	        // Then append as binary
	        this.appendBinary(toUtf8(str));

	        return this;
	    };

	    /**
	     * Appends a binary string.
	     *
	     * @param {String} contents The binary string to be appended
	     *
	     * @return {SparkMD5} The instance itself
	     */
	    SparkMD5.prototype.appendBinary = function (contents) {
	        this._buff += contents;
	        this._length += contents.length;

	        var length = this._buff.length,
	            i;

	        for (i = 64; i <= length; i += 64) {
	            md5cycle(this._hash, md5blk(this._buff.substring(i - 64, i)));
	        }

	        this._buff = this._buff.substring(i - 64);

	        return this;
	    };

	    /**
	     * Finishes the incremental computation, reseting the internal state and
	     * returning the result.
	     *
	     * @param {Boolean} raw True to get the raw string, false to get the hex string
	     *
	     * @return {String} The result
	     */
	    SparkMD5.prototype.end = function (raw) {
	        var buff = this._buff,
	            length = buff.length,
	            i,
	            tail = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	            ret;

	        for (i = 0; i < length; i += 1) {
	            tail[i >> 2] |= buff.charCodeAt(i) << ((i % 4) << 3);
	        }

	        this._finish(tail, length);
	        ret = hex(this._hash);

	        if (raw) {
	            ret = hexToBinaryString(ret);
	        }

	        this.reset();

	        return ret;
	    };

	    /**
	     * Resets the internal state of the computation.
	     *
	     * @return {SparkMD5} The instance itself
	     */
	    SparkMD5.prototype.reset = function () {
	        this._buff = '';
	        this._length = 0;
	        this._hash = [1732584193, -271733879, -1732584194, 271733878];

	        return this;
	    };

	    /**
	     * Gets the internal state of the computation.
	     *
	     * @return {Object} The state
	     */
	    SparkMD5.prototype.getState = function () {
	        return {
	            buff: this._buff,
	            length: this._length,
	            hash: this._hash.slice()
	        };
	    };

	    /**
	     * Gets the internal state of the computation.
	     *
	     * @param {Object} state The state
	     *
	     * @return {SparkMD5} The instance itself
	     */
	    SparkMD5.prototype.setState = function (state) {
	        this._buff = state.buff;
	        this._length = state.length;
	        this._hash = state.hash;

	        return this;
	    };

	    /**
	     * Releases memory used by the incremental buffer and other additional
	     * resources. If you plan to use the instance again, use reset instead.
	     */
	    SparkMD5.prototype.destroy = function () {
	        delete this._hash;
	        delete this._buff;
	        delete this._length;
	    };

	    /**
	     * Finish the final calculation based on the tail.
	     *
	     * @param {Array}  tail   The tail (will be modified)
	     * @param {Number} length The length of the remaining buffer
	     */
	    SparkMD5.prototype._finish = function (tail, length) {
	        var i = length,
	            tmp,
	            lo,
	            hi;

	        tail[i >> 2] |= 0x80 << ((i % 4) << 3);
	        if (i > 55) {
	            md5cycle(this._hash, tail);
	            for (i = 0; i < 16; i += 1) {
	                tail[i] = 0;
	            }
	        }

	        // Do the final computation based on the tail and length
	        // Beware that the final length may not fit in 32 bits so we take care of that
	        tmp = this._length * 8;
	        tmp = tmp.toString(16).match(/(.*?)(.{0,8})$/);
	        lo = parseInt(tmp[2], 16);
	        hi = parseInt(tmp[1], 16) || 0;

	        tail[14] = lo;
	        tail[15] = hi;
	        md5cycle(this._hash, tail);
	    };

	    /**
	     * Performs the md5 hash on a string.
	     * A conversion will be applied if utf8 string is detected.
	     *
	     * @param {String}  str The string
	     * @param {Boolean} [raw] True to get the raw string, false to get the hex string
	     *
	     * @return {String} The result
	     */
	    SparkMD5.hash = function (str, raw) {
	        // Converts the string to utf8 bytes if necessary
	        // Then compute it using the binary function
	        return SparkMD5.hashBinary(toUtf8(str), raw);
	    };

	    /**
	     * Performs the md5 hash on a binary string.
	     *
	     * @param {String}  content The binary string
	     * @param {Boolean} [raw]     True to get the raw string, false to get the hex string
	     *
	     * @return {String} The result
	     */
	    SparkMD5.hashBinary = function (content, raw) {
	        var hash = md51(content),
	            ret = hex(hash);

	        return raw ? hexToBinaryString(ret) : ret;
	    };

	    // ---------------------------------------------------

	    /**
	     * SparkMD5 OOP implementation for array buffers.
	     *
	     * Use this class to perform an incremental md5 ONLY for array buffers.
	     */
	    SparkMD5.ArrayBuffer = function () {
	        // call reset to init the instance
	        this.reset();
	    };

	    /**
	     * Appends an array buffer.
	     *
	     * @param {ArrayBuffer} arr The array to be appended
	     *
	     * @return {SparkMD5.ArrayBuffer} The instance itself
	     */
	    SparkMD5.ArrayBuffer.prototype.append = function (arr) {
	        var buff = concatenateArrayBuffers(this._buff.buffer, arr),
	            length = buff.length,
	            i;

	        this._length += arr.byteLength;

	        for (i = 64; i <= length; i += 64) {
	            md5cycle(this._hash, md5blk_array(buff.subarray(i - 64, i)));
	        }

	        this._buff = (i - 64) < length ? new Uint8Array(buff.buffer.slice(i - 64)) : new Uint8Array(0);

	        return this;
	    };

	    /**
	     * Finishes the incremental computation, reseting the internal state and
	     * returning the result.
	     *
	     * @param {Boolean} raw True to get the raw string, false to get the hex string
	     *
	     * @return {String} The result
	     */
	    SparkMD5.ArrayBuffer.prototype.end = function (raw) {
	        var buff = this._buff,
	            length = buff.length,
	            tail = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	            i,
	            ret;

	        for (i = 0; i < length; i += 1) {
	            tail[i >> 2] |= buff[i] << ((i % 4) << 3);
	        }

	        this._finish(tail, length);
	        ret = hex(this._hash);

	        if (raw) {
	            ret = hexToBinaryString(ret);
	        }

	        this.reset();

	        return ret;
	    };

	    /**
	     * Resets the internal state of the computation.
	     *
	     * @return {SparkMD5.ArrayBuffer} The instance itself
	     */
	    SparkMD5.ArrayBuffer.prototype.reset = function () {
	        this._buff = new Uint8Array(0);
	        this._length = 0;
	        this._hash = [1732584193, -271733879, -1732584194, 271733878];

	        return this;
	    };

	    /**
	     * Gets the internal state of the computation.
	     *
	     * @return {Object} The state
	     */
	    SparkMD5.ArrayBuffer.prototype.getState = function () {
	        var state = SparkMD5.prototype.getState.call(this);

	        // Convert buffer to a string
	        state.buff = arrayBuffer2Utf8Str(state.buff);

	        return state;
	    };

	    /**
	     * Gets the internal state of the computation.
	     *
	     * @param {Object} state The state
	     *
	     * @return {SparkMD5.ArrayBuffer} The instance itself
	     */
	    SparkMD5.ArrayBuffer.prototype.setState = function (state) {
	        // Convert string to buffer
	        state.buff = utf8Str2ArrayBuffer(state.buff, true);

	        return SparkMD5.prototype.setState.call(this, state);
	    };

	    SparkMD5.ArrayBuffer.prototype.destroy = SparkMD5.prototype.destroy;

	    SparkMD5.ArrayBuffer.prototype._finish = SparkMD5.prototype._finish;

	    /**
	     * Performs the md5 hash on an array buffer.
	     *
	     * @param {ArrayBuffer} arr The array buffer
	     * @param {Boolean}     [raw] True to get the raw string, false to get the hex one
	     *
	     * @return {String} The result
	     */
	    SparkMD5.ArrayBuffer.hash = function (arr, raw) {
	        var hash = md51_array(new Uint8Array(arr)),
	            ret = hex(hash);

	        return raw ? hexToBinaryString(ret) : ret;
	    };

	    return SparkMD5;
	})); 
} (sparkMd5));

var sparkMd5Exports = sparkMd5.exports;
const SparkMD5 = /*@__PURE__*/getDefaultExportFromCjs(sparkMd5Exports);

const {defineComponent:_defineComponent} = await importShared('vue');

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,normalizeClass:_normalizeClass,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,unref:_unref,normalizeStyle:_normalizeStyle,createTextVNode:_createTextVNode,withModifiers:_withModifiers,renderList:_renderList,Fragment:_Fragment,vModelText:_vModelText,withDirectives:_withDirectives} = await importShared('vue');

const _hoisted_1 = { class: "cloudimg123-page" };
const _hoisted_2 = { class: "page-header text-center mb-6" };
const _hoisted_3 = { class: "d-flex align-center justify-center mb-2" };
const _hoisted_4 = { class: "stats-bar" };
const _hoisted_5 = { class: "stat-value-and-trend" };
const _hoisted_6 = {
  key: 0,
  class: "stat-trend"
};
const _hoisted_7 = { class: "stat-value-and-trend" };
const _hoisted_8 = {
  key: 0,
  class: "stat-trend"
};
const _hoisted_9 = { class: "stat-value-and-trend" };
const _hoisted_10 = {
  key: 0,
  class: "stat-trend"
};
const _hoisted_11 = { class: "stats-actions" };
const _hoisted_12 = {
  key: 0,
  class: "tooltip"
};
const _hoisted_13 = { class: "tabs-container" };
const _hoisted_14 = { class: "tabs-header" };
const _hoisted_15 = {
  key: 0,
  class: "tab-content upload-tab"
};
const _hoisted_16 = { class: "dropzone-content" };
const _hoisted_17 = {
  key: 0,
  class: "uploading-state"
};
const _hoisted_18 = { class: "progress-bar" };
const _hoisted_19 = { class: "progress-info" };
const _hoisted_20 = { class: "progress-text" };
const _hoisted_21 = {
  viewBox: "0 0 24 24",
  width: "16",
  height: "16",
  style: { "margin-right": "4px" }
};
const _hoisted_22 = {
  key: 0,
  class: "active-indicator"
};
const _hoisted_23 = {
  key: 1,
  class: "idle-state"
};
const _hoisted_24 = { class: "result-header" };
const _hoisted_25 = { class: "filename" };
const _hoisted_26 = { class: "result-content-grid" };
const _hoisted_27 = { class: "thumbnail-section" };
const _hoisted_28 = { class: "thumbnail-container" };
const _hoisted_29 = ["src", "alt"];
const _hoisted_30 = { class: "formats-grid" };
const _hoisted_31 = { class: "format-row" };
const _hoisted_32 = { class: "format-group" };
const _hoisted_33 = { class: "link-item" };
const _hoisted_34 = ["value"];
const _hoisted_35 = ["onClick"];
const _hoisted_36 = { class: "format-group" };
const _hoisted_37 = { class: "link-item" };
const _hoisted_38 = ["value"];
const _hoisted_39 = ["onClick"];
const _hoisted_40 = { class: "format-row" };
const _hoisted_41 = { class: "format-group" };
const _hoisted_42 = { class: "link-item" };
const _hoisted_43 = ["value"];
const _hoisted_44 = ["onClick"];
const _hoisted_45 = { class: "format-group" };
const _hoisted_46 = { class: "link-item" };
const _hoisted_47 = ["value"];
const _hoisted_48 = ["onClick"];
const _hoisted_49 = { class: "result-header" };
const _hoisted_50 = { class: "error-text" };
const _hoisted_51 = {
  key: 1,
  class: "tab-content history-tab"
};
const _hoisted_52 = { class: "history-toolbar" };
const _hoisted_53 = { class: "search-section" };
const _hoisted_54 = { class: "search-input-group" };
const _hoisted_55 = { class: "toolbar-actions" };
const _hoisted_56 = { class: "grid-control" };
const _hoisted_57 = { class: "grid-options" };
const _hoisted_58 = ["onClick"];
const _hoisted_59 = ["disabled"];
const _hoisted_60 = {
  key: 0,
  class: "loading-state"
};
const _hoisted_61 = {
  key: 1,
  class: "empty-state"
};
const _hoisted_62 = {
  key: 2,
  class: "history-list"
};
const _hoisted_63 = {
  key: 0,
  class: "batch-controls"
};
const _hoisted_64 = { class: "checkbox-label" };
const _hoisted_65 = ["checked", "indeterminate"];
const _hoisted_66 = ["onMouseenter"];
const _hoisted_67 = {
  key: 0,
  class: "selection-overlay"
};
const _hoisted_68 = ["checked", "onChange"];
const _hoisted_69 = ["onClick"];
const _hoisted_70 = {
  key: 0,
  class: "thumbnail-generating-indicator"
};
const _hoisted_71 = ["src", "data-src", "data-lazy-type", "data-file-id", "alt", "onError", "onLoad"];
const _hoisted_72 = ["onClick"];
const _hoisted_73 = ["onClick"];
const _hoisted_74 = { class: "file-info" };
const _hoisted_75 = ["title"];
const _hoisted_76 = { class: "meta-info" };
const _hoisted_77 = { class: "file-size" };
const _hoisted_78 = { class: "upload-time" };
const _hoisted_79 = ["onClick"];
const _hoisted_80 = ["onClick"];
const _hoisted_81 = ["onClick"];
const _hoisted_82 = ["onClick"];
const _hoisted_83 = ["onMouseenter"];
const _hoisted_84 = {
  key: 0,
  class: "selection-overlay"
};
const _hoisted_85 = ["checked", "onChange"];
const _hoisted_86 = ["onClick"];
const _hoisted_87 = {
  key: 0,
  class: "thumbnail-generating-indicator"
};
const _hoisted_88 = ["src", "data-src", "data-lazy-type", "data-file-id", "alt", "onError", "onLoad"];
const _hoisted_89 = ["onClick"];
const _hoisted_90 = {
  key: 1,
  class: "image-badge"
};
const _hoisted_91 = { class: "card-content" };
const _hoisted_92 = { class: "file-header" };
const _hoisted_93 = ["title"];
const _hoisted_94 = { class: "file-meta" };
const _hoisted_95 = { class: "file-size" };
const _hoisted_96 = { class: "upload-time" };
const _hoisted_97 = ["onClick"];
const _hoisted_98 = ["onClick"];
const _hoisted_99 = ["onClick"];
const _hoisted_100 = ["onClick"];
const _hoisted_101 = {
  key: 3,
  class: "pagination"
};
const _hoisted_102 = ["disabled"];
const _hoisted_103 = { class: "page-info" };
const _hoisted_104 = ["disabled"];
const _hoisted_105 = { class: "modal-header" };
const _hoisted_106 = { class: "header-left" };
const _hoisted_107 = { class: "preview-file-header" };
const _hoisted_108 = { class: "file-info" };
const _hoisted_109 = {
  key: 0,
  class: "image-position"
};
const _hoisted_110 = { class: "header-right" };
const _hoisted_111 = ["disabled"];
const _hoisted_112 = { class: "modal-body" };
const _hoisted_113 = {
  key: 0,
  class: "image-loader"
};
const _hoisted_114 = ["src", "alt"];
const _hoisted_115 = {
  key: 4,
  class: "image-error"
};
const _hoisted_116 = { class: "modal-syntax-section" };
const _hoisted_117 = { class: "syntax-input-group" };
const _hoisted_118 = { class: "syntax-input-item" };
const _hoisted_119 = ["value"];
const _hoisted_120 = { class: "syntax-input-group" };
const _hoisted_121 = { class: "syntax-input-item" };
const _hoisted_122 = ["value"];
const _hoisted_123 = { class: "syntax-input-group" };
const _hoisted_124 = { class: "syntax-input-item" };
const _hoisted_125 = ["value"];
const _hoisted_126 = { class: "syntax-input-group" };
const _hoisted_127 = { class: "syntax-input-item" };
const _hoisted_128 = ["value"];
const _hoisted_129 = { class: "modal-header" };
const _hoisted_130 = { class: "header-left" };
const _hoisted_131 = { class: "task-summary" };
const _hoisted_132 = { class: "header-right" };
const _hoisted_133 = ["disabled"];
const _hoisted_134 = {
  viewBox: "0 0 24 24",
  width: "16",
  height: "16",
  style: { "margin-right": "4px" }
};
const _hoisted_135 = { class: "upload-list-content" };
const _hoisted_136 = {
  key: 0,
  class: "empty-upload-list"
};
const _hoisted_137 = {
  key: 1,
  class: "upload-task-list"
};
const _hoisted_138 = { class: "task-main-info" };
const _hoisted_139 = ["title"];
const _hoisted_140 = { class: "task-status" };
const _hoisted_141 = { class: "task-progress-info" };
const _hoisted_142 = { class: "task-progress-bar" };
const _hoisted_143 = { class: "task-progress-text" };
const _hoisted_144 = { class: "task-actions" };
const _hoisted_145 = ["onClick"];
const _hoisted_146 = ["title"];
const _hoisted_147 = {
  key: 0,
  viewBox: "0 0 24 24",
  width: "20",
  height: "20"
};
const _hoisted_148 = {
  key: 1,
  viewBox: "0 0 24 24",
  width: "20",
  height: "20"
};
const {ref,onMounted,onUnmounted,computed,watch,nextTick} = await importShared('vue');
const MAX_CONCURRENT_THUMBNAILS = 3;
const _sfc_main = /* @__PURE__ */ _defineComponent({
  __name: "Page",
  props: {
    api: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ["action", "switch", "close"],
  setup(__props, { emit: __emit }) {
    class FileHashManager {
      constructor() {
        this.hashCache = /* @__PURE__ */ new Map();
      }
      async calculateFileHash(file) {
        return new Promise((resolve) => {
          const reader = new FileReader();
          const spark = new SparkMD5.ArrayBuffer();
          reader.onload = async (e) => {
            spark.append(e.target.result);
            const hash = spark.end();
            this.hashCache.set(file.name, {
              hash,
              size: file.size,
              lastModified: file.lastModified
            });
            resolve(hash);
          };
          reader.readAsArrayBuffer(file);
        });
      }
      async checkDuplicateInHistory(file, historyItems2) {
        const hash = await this.calculateFileHash(file);
        const duplicateRecord = historyItems2.find((record) => record.file_hash === hash);
        return {
          isDuplicate: !!duplicateRecord,
          hash,
          existingRecord: duplicateRecord
        };
      }
      getHashCache() {
        return Array.from(this.hashCache.entries());
      }
      clearCache() {
        this.hashCache.clear();
      }
    }
    const escapeHtml = (text) => {
      if (!text) return "";
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    };
    const props = __props;
    const emit = __emit;
    let lazyLoadObserver = null;
    const setupLazyLoading = () => {
      console.log("[懒加载调试] setupLazyLoading 被调用");
      if (lazyLoadObserver) {
        lazyLoadObserver.destroy();
        console.log("[懒加载调试] 销毁旧的懒加载观察器");
      }
      const { observeImage, unobserveImage, destroy } = useImageLazyLoad();
      lazyLoadObserver = { observeImage, unobserveImage, destroy };
      console.log("[懒加载调试] 创建新的懒加载观察器");
      if (document._hasThumbnailListener) {
        document.removeEventListener("lazy-load-thumbnail", handleLazyLoadThumbnail);
        document._hasThumbnailListener = false;
        console.log("[懒加载调试] 移除旧的缩略图懒加载事件监听器");
      }
      nextTick(() => {
        const lazyImages = document.querySelectorAll("img[data-src]");
        console.log("[懒加载调试] 找到懒加载图片数量:", lazyImages.length);
        lazyImages.forEach((img) => {
          console.log("[懒加载调试] 设置懒加载图片:", {
            src: img.src,
            dataSrc: img.dataset.src,
            fileId: img.dataset.fileId,
            lazyType: img.dataset.lazyType
          });
          lazyLoadObserver.observeImage(img);
        });
        document.addEventListener("lazy-load-thumbnail", handleLazyLoadThumbnail);
        document._hasThumbnailListener = true;
        console.log("[懒加载调试] 添加缩略图懒加载事件监听器");
      });
    };
    const handleLazyLoadThumbnail = async (event) => {
      const { img, fileId } = event.detail;
      console.log("[懒加载调试] 收到缩略图懒加载事件:", { fileId, img });
      try {
        console.log("[懒加载调试] 开始获取缩略图:", fileId);
        const thumbnailUrl = await getThumbnailViaApi(fileId);
        console.log("[懒加载调试] 缩略图获取结果:", { fileId, hasThumbnail: !!thumbnailUrl, thumbnailUrl: thumbnailUrl?.substring(0, 100) + "..." });
        if (thumbnailUrl) {
          console.log("[懒加载调试] 准备设置img.src:", fileId);
          console.log("[懒加载调试] 设置前的img.src:", img.src);
          console.log("[懒加载调试] 设置前的img.dataset.src:", img.dataset.src);
          img.src = thumbnailUrl;
          img.removeAttribute("data-src");
          console.log("[懒加载调试] 设置缩略图URL成功:", fileId);
          console.log("[懒加载调试] 设置后的img.src:", img.src.substring(0, 100) + "...");
          img.onload = () => {
            console.log("[懒加载调试] 缩略图加载完成，取消观察:", fileId);
            img.classList.add("lazy-loaded");
            if (lazyLoadObserver && lazyLoadObserver.unobserveImage) {
              lazyLoadObserver.unobserveImage(img);
            }
          };
          img.onerror = () => {
            console.warn("[懒加载调试] 缩略图加载失败，使用原图:", fileId);
            img.classList.add("lazy-error");
            if (lazyLoadObserver && lazyLoadObserver.unobserveImage) {
              lazyLoadObserver.unobserveImage(img);
            }
            const item = historyItems.value.find((item2) => item2.file_id === fileId);
            if (item && item.download_url) {
              img.src = item.download_url;
            }
          };
          const itemIndex = historyItems.value.findIndex((item) => item.file_id === fileId);
          if (itemIndex !== -1) {
            const updatedItem = { ...historyItems.value[itemIndex], _cachedUrl: thumbnailUrl };
            const newHistoryItems = [...historyItems.value];
            newHistoryItems[itemIndex] = updatedItem;
            historyItems.value = newHistoryItems;
          }
        } else {
          console.log("[懒加载调试] 缩略图获取失败，使用原图:", fileId);
          const item = historyItems.value.find((item2) => item2.file_id === fileId);
          if (item && item.download_url) {
            img.src = item.download_url;
            img.removeAttribute("data-src");
          }
          if (lazyLoadObserver && lazyLoadObserver.unobserveImage) {
            lazyLoadObserver.unobserveImage(img);
          }
        }
      } catch (error) {
        console.warn("懒加载缩略图失败:", error);
        const item = historyItems.value.find((item2) => item2.file_id === fileId);
        if (item && item.download_url) {
          img.src = item.download_url;
          img.removeAttribute("data-src");
        }
        if (lazyLoadObserver && lazyLoadObserver.unobserveImage) {
          lazyLoadObserver.unobserveImage(img);
        }
      }
    };
    const historyItems = ref([]);
    const filteredItems = ref([]);
    const searchQuery = ref("");
    const isLoading = ref(false);
    const currentPage = ref(1);
    const itemsPerPage = ref(20);
    const selectedItems = ref([]);
    const isDeleteMode = ref(false);
    const previewImage = ref(null);
    const showPreview = ref(false);
    const previewState = ref({
      images: [],
      currentIndex: 0,
      visible: false
    });
    const imagesPerRow = ref(4);
    const gridOptions = [2, 3, 4, 5, 6];
    const showGridSelector = ref(false);
    const selectGridOption = (option) => {
      setImagesPerRow(option);
      showGridSelector.value = false;
    };
    const ENABLE_VIRTUAL_SCROLL = computed(() => {
      return filteredItems.value ? filteredItems.value.length > 50 : false;
    });
    const cardWidth = computed(() => {
      const isMobile = window.innerWidth <= 768;
      if (isMobile) {
        return window.innerWidth - 32;
      }
      const containerWidth = 1200;
      const gap = 20;
      return Math.floor((containerWidth - gap * (imagesPerRow.value - 1)) / imagesPerRow.value);
    });
    const virtualCardHeight = computed(() => {
      const isMobile = window.innerWidth <= 768;
      return isMobile ? 132 : 300;
    });
    const virtualCardGap = computed(() => {
      const isMobile = window.innerWidth <= 768;
      return isMobile ? 12 : 20;
    });
    computed(() => {
      const isMobile = window.innerWidth <= 768;
      return isMobile ? 1 : imagesPerRow.value;
    });
    const virtualContainerWidth = computed(() => {
      const isMobile = window.innerWidth <= 768;
      return isMobile ? window.innerWidth : 1200;
    });
    const {
      containerRef: virtualContainerRef,
      visibleItems: virtualVisibleItems,
      containerStyle: virtualContainerStyle,
      contentStyle: virtualContentStyle,
      resetScroll: resetVirtualScroll,
      recalculateLayout: recalculateVirtualLayout
    } = useVirtualGrid(filteredItems, cardWidth, virtualCardHeight, virtualCardGap, virtualContainerWidth);
    watch(virtualVisibleItems, () => {
      if (ENABLE_VIRTUAL_SCROLL.value) {
        nextTick(() => {
          if (lazyLoadObserver) {
            const lazyImages = document.querySelectorAll("img[data-src]:not([data-lazy-observed])");
            lazyImages.forEach((img) => {
              lazyLoadObserver.observeImage(img);
              img.setAttribute("data-lazy-observed", "true");
            });
          }
        });
      }
    }, { deep: true });
    const isRefreshing = ref(false);
    const showConfigTip = ref(false);
    const hoveredStat = ref("");
    const tabHover = ref("");
    const btnHover = ref("");
    const copiedLink = ref("");
    const showNotification = ref(false);
    const notificationMessage = ref("");
    const notificationType = ref("success");
    const totalFiles = ref(0);
    const cardHover = ref(null);
    const isImageLoading = ref(false);
    const currentTab = ref("upload");
    const isDragOver = ref(false);
    const isUploading = ref(false);
    const uploadProgress = ref(0);
    const uploadResults = ref([]);
    const uploadErrors = ref([]);
    const uploadTasks = ref([]);
    const activeUploads = ref(0);
    const showUploadList = ref(false);
    const statistics = ref({
      totalUploads: 0,
      totalSize: 0,
      todayUploads: 0
    });
    const totalPages = computed(() => {
      return Math.ceil(filteredItems.value.length / itemsPerPage.value);
    });
    const paginatedItems = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value;
      const end = start + itemsPerPage.value;
      return filteredItems.value.slice(start, end);
    });
    const hasSelection = computed(() => {
      return selectedItems.value.length > 0;
    });
    const isSelected = (item) => {
      return selectedItems.value.some((selected) => selected.file_id === item.file_id);
    };
    const gridStyle = computed(() => {
      return {
        gridTemplateColumns: `repeat(${imagesPerRow.value}, 1fr)`
      };
    });
    const showNotificationMessage = (message, type = "success", duration = 3e3) => {
      notificationMessage.value = message;
      notificationType.value = type;
      showNotification.value = true;
      setTimeout(() => {
        showNotification.value = false;
      }, duration);
    };
    const copyLink = async (link, format) => {
      const success = await copyToClipboard(link);
      if (success) {
        copiedLink.value = link;
        showNotificationMessage(`${format}链接已复制到剪贴板`, "success");
        setTimeout(() => {
          if (copiedLink.value === link) {
            copiedLink.value = "";
          }
        }, 3e3);
      } else {
        showNotificationMessage("复制失败，请手动复制", "error");
      }
    };
    const clearResults = () => {
      uploadResults.value = [];
      uploadErrors.value = [];
    };
    const selectAll = (event) => {
      event.target.select();
    };
    const extractImageUrl = (url) => {
      if (!url) return "";
      if (url.includes("<img") && url.includes('src="')) {
        const match = url.match(/src="([^"]+)"/);
        return match ? match[1] : url;
      }
      if (url.includes("![") && url.includes("](")) {
        const match = url.match(/\]\(([^)]+)\)/);
        return match ? match[1] : url;
      }
      if (url.includes("[img]") && url.includes("[/img]")) {
        const match = url.match(/\[img\]([^\[]+)\[\/img\]/);
        return match ? match[1] : url;
      }
      return url;
    };
    const handleThumbnailError = (event) => {
      const target = event.target;
      target.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0zNSA0MEw0NSAzMEw2NSA1MEw4MCAzNUw5NSA1MEw5NSA4MEg1VjcwTDMwIDU1TDM1IDQwWiIgZmlsbD0iI0Q5RDlEOSIvPgo8Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSI2IiBmaWxsPSIjRDlEOUQ5Ii8+Cjx0ZXh0IHg9IjUwIiB5PSI1NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzk5OTk5OSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEwIj7nlJ/mtLvotb/kuIrkuIDopoHkuI3lm77niYc8L3RleHQ+Cjwvc3ZnPg==";
      target.alt = "图片预览加载失败";
    };
    const downloadImage = (url, filename) => {
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showNotificationMessage(`开始下载: ${filename}`, "success");
    };
    const handleFileSelect = (event) => {
      const target = event.target;
      if (target.files) {
        handleFiles(Array.from(target.files));
      }
    };
    const handleDrop = (event) => {
      event.preventDefault();
      isDragOver.value = false;
      if (event.dataTransfer?.files) {
        handleFiles(Array.from(event.dataTransfer.files));
      }
    };
    const handleDragOver = (event) => {
      event.preventDefault();
      isDragOver.value = true;
    };
    const handleDragLeave = (event) => {
      event.preventDefault();
      isDragOver.value = false;
    };
    const generateId = () => {
      return Date.now().toString(36) + Math.random().toString(36).substr(2);
    };
    const createUploadTask = (file) => {
      return {
        id: generateId(),
        file,
        filename: file.name,
        progress: 0,
        status: "pending",
        controller: new AbortController(),
        isDuplicate: false,
        fileHash: "",
        existingRecord: null,
        message: ""
      };
    };
    const cancelUpload = (taskId) => {
      const task = uploadTasks.value.find((t) => t.id === taskId);
      if (task && task.controller && task.status === "uploading") {
        task.controller.abort();
        task.status = "cancelled";
        activeUploads.value--;
        if (activeUploads.value === 0) {
          isUploading.value = false;
        }
        showNotificationMessage(`已取消上传: ${task.filename}`, "info");
      }
    };
    const cancelAllUploads = () => {
      uploadTasks.value.forEach((task) => {
        if (task.controller && task.status === "uploading") {
          task.controller.abort();
          task.status = "cancelled";
        }
      });
      activeUploads.value = 0;
      isUploading.value = false;
      showNotificationMessage("已取消所有上传任务", "info");
    };
    const openUploadList = () => {
      showUploadList.value = true;
    };
    const closeUploadList = () => {
      showUploadList.value = false;
    };
    const updateUploadProgress = () => {
      if (uploadTasks.value.length === 0) {
        uploadProgress.value = 0;
        return;
      }
      const totalProgress = uploadTasks.value.reduce((sum, task) => {
        return sum + task.progress;
      }, 0);
      uploadProgress.value = Math.round(totalProgress / uploadTasks.value.length);
    };
    const handleFiles = async (files) => {
      if (isUploading.value) return;
      uploadResults.value = [];
      uploadErrors.value = [];
      totalFiles.value = files.length;
      const validTasks = [];
      const fileHashManager = new FileHashManager();
      for (const file of files) {
        const validation = validateImageFile(file);
        if (validation.valid) {
          const duplicateCheck = await fileHashManager.checkDuplicateInHistory(file, historyItems.value);
          const task = createUploadTask(file);
          if (duplicateCheck.isDuplicate) {
            task.status = "duplicate";
            task.isDuplicate = true;
            task.existingRecord = duplicateCheck.existingRecord;
            task.fileHash = duplicateCheck.hash;
            task.message = "云盘已存在";
          } else {
            task.fileHash = duplicateCheck.hash;
          }
          uploadTasks.value.push(task);
          validTasks.push(task);
        } else {
          uploadErrors.value.push(`${file.name}: ${validation.message}`);
        }
      }
      if (validTasks.length === 0) {
        return;
      }
      isUploading.value = true;
      activeUploads.value = validTasks.length;
      try {
        const uploadPromises = validTasks.map(async (task, index) => {
          if (task.isDuplicate) {
            task.status = "completed";
            task.progress = 100;
            activeUploads.value--;
            uploadResults.value.push({
              filename: task.filename,
              success: true,
              isDuplicate: true,
              links: task.existingRecord.formats || {
                url: task.existingRecord.download_url || "#",
                html: `<img src="${task.existingRecord.download_url || "#"}" alt="${task.filename}">`,
                markdown: `![${task.filename}](${task.existingRecord.download_url || "#"})`,
                bbcode: `[img]${task.existingRecord.download_url || "#"}[/img]`
              }
            });
            console.log(`文件已存在，跳过上传: ${task.filename}`);
            return;
          }
          task.status = "uploading";
          try {
            console.log(`开始上传文件: ${task.filename}`);
            const formData = new FormData();
            formData.append("file", task.file);
            formData.append("file_hash", task.fileHash);
            const result = await props.api.post("plugin/CloudImg123/upload", formData, {
              signal: task.controller?.signal
            });
            console.log(`上传结果:`, result);
            if (result?.success) {
              task.status = "completed";
              task.progress = 100;
              uploadResults.value.push({
                filename: task.filename,
                success: true,
                isDuplicate: false,
                links: result.data.formats || {
                  url: result.data.download_url || "#",
                  html: `<img src="${result.data.download_url || "#"}" alt="${task.filename}">`,
                  markdown: `![${task.filename}](${result.data.download_url || "#"})`,
                  bbcode: `[img]${result.data.download_url || "#"}[/img]`
                }
              });
              if (result.data?.file_id) {
                if (activeThumbnailGenerations.value.size < MAX_CONCURRENT_THUMBNAILS && !activeThumbnailGenerations.value.has(result.data.file_id)) {
                  activeThumbnailGenerations.value.add(result.data.file_id);
                  generateThumbnail(result.data.file_id, true).finally(() => {
                    activeThumbnailGenerations.value.delete(result.data.file_id);
                  }).catch((error) => {
                    console.warn(`自动生成缩略图失败 ${task.filename}:`, error);
                  });
                } else {
                  console.log(`上传后缩略图生成已达到并发限制，跳过: ${task.filename}`);
                }
              }
              console.log(`文件上传成功: ${task.filename}`);
            } else {
              throw new Error(result?.message || "上传失败");
            }
          } catch (error) {
            if (error.name === "AbortError") {
              task.status = "cancelled";
              console.log(`文件上传已取消: ${task.filename}`);
            } else {
              task.status = "error";
              task.error = error.message || "上传失败";
              uploadErrors.value.push(`${task.filename}: ${task.error}`);
              console.error(`上传文件时发生错误: ${task.filename}`, error);
            }
          } finally {
            activeUploads.value--;
            updateUploadProgress();
          }
        });
        await Promise.all(uploadPromises);
        if (uploadResults.value.length > 0) {
          await getHistory();
          await getStatistics();
          const successCount = uploadResults.value.filter((r) => r.success).length;
          const duplicateCount = uploadResults.value.filter((r) => r.isDuplicate).length;
          const newUploadCount = successCount - duplicateCount;
          let message = `成功处理 ${successCount} 张图片`;
          if (duplicateCount > 0) {
            message += `（其中 ${duplicateCount} 张已存在）`;
          }
          if (newUploadCount > 0) {
            message += `，新上传 ${newUploadCount} 张`;
          }
          showNotificationMessage(message, "success");
        }
        if (uploadErrors.value.length > 0) {
          showNotificationMessage(`有 ${uploadErrors.value.length} 张图片上传失败`, "error");
        }
      } catch (error) {
        console.error("批量上传过程中发生错误:", error);
        uploadErrors.value.push(`批量上传失败: ${error.message || "未知错误"}`);
      } finally {
        uploadTasks.value = uploadTasks.value.filter(
          (task) => task.status === "pending" || task.status === "uploading"
        );
        if (activeUploads.value === 0) {
          isUploading.value = false;
        }
        console.log("批量上传完成");
      }
    };
    const getThumbnailViaApi = async (fileId) => {
      try {
        console.log("[缩略图调试] 开始请求缩略图API:", fileId);
        const response = await props.api.get(`plugin/CloudImg123/thumbnail/${fileId}.webp`);
        console.log("[缩略图调试] API响应:", response);
        if (response.success && response.data) {
          console.log("[缩略图调试] 响应数据详情:", {
            mime_type: response.data.mime_type,
            content_length: response.data.content?.length,
            content_preview: response.data.content?.substring(0, 50) + "...",
            size: response.data.size
          });
          const base64Url = `data:${response.data.mime_type};base64,${response.data.content}`;
          console.log("[缩略图调试] 构建的base64 URL:", base64Url.substring(0, 100) + "...");
          return base64Url;
        } else {
          console.log("[缩略图调试] API响应但没有数据:", response);
        }
      } catch (error) {
        console.warn("[缩略图调试] 获取缩略图失败:", error);
      }
      return null;
    };
    const tryThumbnailApi = async (event, item) => {
      console.log(`[缩略图调试] 开始尝试获取缩略图: ${item.original_name}`);
      console.log(`[缩略图调试] 项目信息:`, {
        file_id: item.file_id,
        has_local_thumbnail: item.has_local_thumbnail,
        _hasThumbnailToTry: item._hasThumbnailToTry,
        _thumbnailTried: item._thumbnailTried,
        download_url: item.download_url
      });
      try {
        const thumbnailUrl = await getThumbnailViaApi(item.file_id);
        if (thumbnailUrl) {
          console.log(`缩略图获取成功: ${item.original_name}`);
          event.target.src = thumbnailUrl;
          item._cachedUrl = thumbnailUrl;
          const itemIndex = historyItems.value.findIndex((historyItem) => historyItem.file_id === item.file_id);
          if (itemIndex !== -1) {
            const updatedItem = { ...item, _cachedUrl: thumbnailUrl };
            const newHistoryItems = [...historyItems.value];
            newHistoryItems[itemIndex] = updatedItem;
            historyItems.value = newHistoryItems;
          }
        } else {
          console.log(`缩略图获取失败，使用占位图: ${item.original_name}`);
          showPlaceholderImage(event, item);
          item._errorHandled = true;
          const itemIndex = historyItems.value.findIndex((historyItem) => historyItem.file_id === item.file_id);
          if (itemIndex !== -1) {
            const updatedItem = { ...item, isInvalid: true, _errorHandled: true };
            const newHistoryItems = [...historyItems.value];
            newHistoryItems[itemIndex] = updatedItem;
            historyItems.value = newHistoryItems;
          }
        }
      } catch (error) {
        console.error("缩略图API调用异常:", error);
        showPlaceholderImage(event, item);
        item._errorHandled = true;
        const itemIndex = historyItems.value.findIndex((historyItem) => historyItem.file_id === item.file_id);
        if (itemIndex !== -1) {
          const updatedItem = { ...item, isInvalid: true, _errorHandled: true };
          const newHistoryItems = [...historyItems.value];
          newHistoryItems[itemIndex] = updatedItem;
          historyItems.value = newHistoryItems;
        }
      }
      const errorKey = `${item.file_id}_${event.target.src}`;
      setTimeout(() => {
        globalErrorHandling.value.delete(errorKey);
      }, 1e3);
    };
    const getBestImageUrl = (item) => {
      if (item._cachedUrl) {
        return item._cachedUrl;
      }
      if (item.isInvalid) {
        item._cachedUrl = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
        return item._cachedUrl;
      }
      const placeholderUrl = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
      let actualUrl;
      if (item.has_local_thumbnail && item.file_id) {
        actualUrl = "lazy-thumbnail:" + item.file_id;
        item._hasThumbnailToTry = true;
        item._thumbnailTried = false;
        item._useThumbnailOnly = true;
        console.log(`[缩略图调试] 项目 ${item.original_name} 有本地缩略图，将使用懒加载缩略图`);
      } else {
        actualUrl = item.download_url;
        console.log(`[缩略图调试] 项目 ${item.original_name} 没有本地缩略图，使用懒加载原图`);
      }
      if (!actualUrl || actualUrl === "undefined" || actualUrl === "null") {
        actualUrl = item.download_url || placeholderUrl;
      }
      if (actualUrl.startsWith("lazy-thumbnail:")) {
        item._cachedUrl = placeholderUrl;
        item._lazyActualUrl = actualUrl.replace("lazy-thumbnail:", "");
        item._lazyType = "thumbnail";
      } else {
        item._cachedUrl = placeholderUrl;
        item._lazyActualUrl = actualUrl;
        item._lazyType = "original";
      }
      return placeholderUrl;
    };
    const handleImageError = (event, item) => {
      event.target.onerror = null;
      const errorKey = `${item.file_id}_${event.target.src}`;
      if (globalErrorHandling.value.has(errorKey)) {
        console.log(`错误已在处理中，跳过: ${item.original_name}`);
        return;
      }
      globalErrorHandling.value.add(errorKey);
      console.warn(`图片加载失败: ${item.original_name}`, {
        attempted_url: event.target.src,
        item_data: item
      });
      if (!item._errorHandled) {
        if (item._hasThumbnailToTry && !item._thumbnailTried) {
          item._thumbnailTried = true;
          tryThumbnailApi(event, item);
          return;
        }
        item._errorHandled = true;
        if (item._useThumbnailOnly) {
          console.log(`[缩略图调试] 项目 ${item.original_name} 缩略图获取失败，显示占位图`);
          showPlaceholderImage(event, item);
          return;
        }
        const itemIndex = historyItems.value.findIndex((historyItem) => historyItem.file_id === item.file_id);
        if (itemIndex !== -1) {
          const updatedItem = { ...item, isInvalid: true, _errorHandled: true };
          const newHistoryItems = [...historyItems.value];
          newHistoryItems[itemIndex] = updatedItem;
          historyItems.value = newHistoryItems;
        }
        const errorMessage = `${item.original_name}: 图片链接已失效`;
        if (!uploadErrors.value.includes(errorMessage)) {
          uploadErrors.value.push(errorMessage);
        }
      }
      showPlaceholderImage(event, item);
      setTimeout(() => {
        globalErrorHandling.value.delete(errorKey);
      }, 1e3);
    };
    const showPlaceholderImage = (event, item) => {
      event.target.onerror = null;
      event.target.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
      event.target.alt = `图片链接失效: ${item.original_name}`;
      event.target.style.filter = "opacity(0.6)";
      event.target.style.backgroundColor = "var(--surface-color)";
      event.target.style.objectFit = "contain";
      event.target.onload = null;
      event.target.onerror = null;
    };
    const activeThumbnailGenerations = ref(/* @__PURE__ */ new Set());
    const thumbnailGenerationDebounce = ref(/* @__PURE__ */ new Map());
    const globalErrorHandling = ref(/* @__PURE__ */ new Set());
    const handleImageLoad = (event, item) => {
      event.target.onerror = null;
      event.target.style.filter = "";
      if (item.isInvalid) {
        const itemIndex = historyItems.value.findIndex((historyItem) => historyItem.file_id === item.file_id);
        if (itemIndex !== -1) {
          const updatedItem = { ...item, isInvalid: false, _errorHandled: false };
          const newHistoryItems = [...historyItems.value];
          newHistoryItems[itemIndex] = updatedItem;
          historyItems.value = newHistoryItems;
        }
        const errorMessage = `${item.original_name}: 图片链接已失效`;
        const errorIndex = uploadErrors.value.indexOf(errorMessage);
        if (errorIndex > -1) {
          uploadErrors.value.splice(errorIndex, 1);
        }
      }
      if (!item.has_local_thumbnail && event.target.src === item.download_url) {
        console.log(`检测到原图加载但没有本地缩略图，自动生成: ${item.original_name}`);
        if (thumbnailGenerationDebounce.value.has(item.file_id)) {
          clearTimeout(thumbnailGenerationDebounce.value.get(item.file_id));
        }
        if (activeThumbnailGenerations.value.size < MAX_CONCURRENT_THUMBNAILS && !activeThumbnailGenerations.value.has(item.file_id)) {
          activeThumbnailGenerations.value.add(item.file_id);
          const timer = setTimeout(() => {
            generateThumbnail(item.file_id, true).finally(() => {
              activeThumbnailGenerations.value.delete(item.file_id);
              thumbnailGenerationDebounce.value.delete(item.file_id);
            }).catch((error) => {
              console.warn(`自动生成缩略图失败 ${item.original_name}:`, error);
            });
          }, 1e3);
          thumbnailGenerationDebounce.value.set(item.file_id, timer);
        } else {
          console.log(`缩略图生成已达到并发限制或已在生成中，跳过: ${item.original_name}`);
        }
      }
    };
    const handleModalImageLoad = (event) => {
      isImageLoading.value = false;
      if (previewImage.value && !previewImage.value.has_local_thumbnail) {
        console.log(`弹窗检测到原图加载但没有本地缩略图，自动生成: ${previewImage.value.original_name}`);
        if (thumbnailGenerationDebounce.value.has(previewImage.value.file_id)) {
          clearTimeout(thumbnailGenerationDebounce.value.get(previewImage.value.file_id));
        }
        if (activeThumbnailGenerations.value.size < MAX_CONCURRENT_THUMBNAILS && !activeThumbnailGenerations.value.has(previewImage.value.file_id)) {
          activeThumbnailGenerations.value.add(previewImage.value.file_id);
          const timer = setTimeout(() => {
            generateThumbnail(previewImage.value.file_id, true).finally(() => {
              activeThumbnailGenerations.value.delete(previewImage.value.file_id);
              thumbnailGenerationDebounce.value.delete(previewImage.value.file_id);
            }).catch((error) => {
              console.warn(`弹窗自动生成缩略图失败 ${previewImage.value.original_name}:`, error);
            });
          }, 1e3);
          thumbnailGenerationDebounce.value.set(previewImage.value.file_id, timer);
        } else {
          console.log(`弹窗缩略图生成已达到并发限制或已在生成中，跳过: ${previewImage.value.original_name}`);
        }
      }
    };
    const handleModalImageError = (event) => {
      event.target.onerror = null;
      console.warn(`弹窗图片加载失败: ${previewImage.value?.original_name}`);
      event.target.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
      event.target.style.filter = "opacity(0.6)";
      event.target.style.backgroundColor = "var(--surface-color)";
      event.target.style.objectFit = "contain";
      if (previewImage.value) {
        previewImage.value = { ...previewImage.value, isInvalid: true, _errorHandled: true };
      }
      isImageLoading.value = false;
    };
    const getHistory = async () => {
      if (isLoading.value) return;
      isLoading.value = true;
      try {
        const response = await props.api.get("plugin/CloudImg123/history");
        if (response.success && response.data) {
          historyItems.value = (response.data || []).map((item) => ({
            ...item,
            isInvalid: false,
            isGeneratingThumbnail: false,
            // 添加缩略图生成状态
            _cachedUrl: void 0,
            // 清除URL缓存
            _errorHandled: false,
            // 添加错误处理标记
            _errorRetryCount: 0,
            // 重置错误重试计数
            _lazyActualUrl: void 0,
            // 清除懒加载URL
            _lazyType: void 0
            // 清除懒加载类型
          }));
        } else {
          historyItems.value = [];
        }
        filterItems();
        nextTick(() => {
          console.log("[懒加载调试] 开始设置懒加载，历史记录数量:", historyItems.value.length);
          setupLazyLoading();
          console.log("[懒加载调试] 懒加载设置完成");
          if (typeof resetVirtualScroll === "function") {
            resetVirtualScroll();
            console.log("[懒加载调试] 虚拟滚动重置完成");
          }
          if (typeof recalculateVirtualLayout === "function") {
            recalculateVirtualLayout();
            console.log("[懒加载调试] 虚拟布局重新计算完成");
          }
        });
      } catch (error) {
        console.error("获取历史记录失败:", error);
        historyItems.value = [];
        const errorMessage = error.response?.data?.message || error.message || "获取历史记录失败";
        showNotificationMessage(`获取历史记录失败: ${errorMessage}`, "error");
      } finally {
        isLoading.value = false;
      }
    };
    const generateThumbnail = async (fileId, isAutoGeneration = false, retryCount = 0) => {
      const maxRetries = 2;
      try {
        const targetItemIndex = historyItems.value.findIndex((item) => item.file_id === fileId);
        if (targetItemIndex !== -1) {
          const targetItem = historyItems.value[targetItemIndex];
          historyItems.value[targetItemIndex] = {
            ...targetItem,
            isGeneratingThumbnail: true,
            thumbnailRetryCount: retryCount
          };
        }
        if (!isAutoGeneration) {
          showNotificationMessage("正在生成缩略图...", "info");
        }
        const response = await props.api.post(`plugin/CloudImg123/thumbnail/generate`, { file_id: fileId });
        if (targetItemIndex !== -1) {
          const targetItem = historyItems.value[targetItemIndex];
          const newHistoryItems = [...historyItems.value];
          const { isGeneratingThumbnail, thumbnailRetryCount, ...rest } = targetItem;
          newHistoryItems[targetItemIndex] = rest;
          historyItems.value = newHistoryItems;
        }
        if (response.success) {
          if (!isAutoGeneration) {
            showNotificationMessage("缩略图生成成功", "success");
          }
          if (!isAutoGeneration) {
            setTimeout(async () => {
              await getHistory();
            }, 500);
          } else {
            const targetItemIndex2 = historyItems.value.findIndex((item) => item.file_id === fileId);
            if (targetItemIndex2 !== -1) {
              const targetItem = historyItems.value[targetItemIndex2];
              delete targetItem._cachedUrl;
              try {
                const recordResponse = await props.api.get(`plugin/CloudImg123/history?file_id=${fileId}`);
                if (recordResponse.success && recordResponse.data && recordResponse.data.length > 0) {
                  const record = recordResponse.data[0];
                  const newHistoryItems = [...historyItems.value];
                  newHistoryItems[targetItemIndex2] = {
                    ...targetItem,
                    has_local_thumbnail: true,
                    thumbnail_url: record.thumbnail_url,
                    isInvalid: false,
                    // 重置无效状态
                    _errorHandled: false
                    // 重置错误处理标记
                  };
                  historyItems.value = newHistoryItems;
                }
              } catch (error) {
                console.warn("获取更新后的缩略图URL失败:", error);
              }
            }
          }
        } else {
          if (retryCount < maxRetries) {
            console.log(`缩略图生成失败，进行第 ${retryCount + 1} 次重试: ${fileId}`);
            setTimeout(() => {
              generateThumbnail(fileId, isAutoGeneration, retryCount + 1);
            }, 1e3 * (retryCount + 1));
          } else {
            showNotificationMessage(`缩略图生成失败: ${response.message}`, "error");
          }
        }
      } catch (error) {
        console.error("生成缩略图失败:", error);
        const targetItemIndex = historyItems.value.findIndex((item) => item.file_id === fileId);
        if (targetItemIndex !== -1) {
          const targetItem = historyItems.value[targetItemIndex];
          const newHistoryItems = [...historyItems.value];
          const { isGeneratingThumbnail, thumbnailRetryCount, ...rest } = targetItem;
          newHistoryItems[targetItemIndex] = rest;
          historyItems.value = newHistoryItems;
        }
        if (retryCount < maxRetries) {
          console.log(`网络错误，进行第 ${retryCount + 1} 次重试: ${fileId}`);
          setTimeout(() => {
            generateThumbnail(fileId, isAutoGeneration, retryCount + 1);
          }, 1e3 * (retryCount + 1));
        } else {
          showNotificationMessage("缩略图生成失败: 网络错误", "error");
        }
      }
    };
    const filterItems = () => {
      if (!searchQuery.value.trim()) {
        filteredItems.value = historyItems.value;
        console.log("[搜索调试] 清空搜索，使用原始数组");
      } else {
        const query = searchQuery.value.toLowerCase();
        filteredItems.value = historyItems.value.filter(
          (item) => item.original_name?.toLowerCase().includes(query) || item.file_name?.toLowerCase().includes(query)
        );
        console.log("[搜索调试] 搜索过滤完成，结果数量:", filteredItems.value.length);
        if (filteredItems.value.length > 0) {
          const firstItem = filteredItems.value[0];
          console.log("[搜索调试] 第一个过滤结果的懒加载属性:", {
            original_name: firstItem.original_name,
            _lazyActualUrl: firstItem._lazyActualUrl,
            _lazyType: firstItem._lazyType,
            _cachedUrl: firstItem._cachedUrl
          });
        }
      }
      currentPage.value = 1;
    };
    const previewItem = (item) => {
      const currentImages = paginatedItems.value;
      previewState.value = {
        images: currentImages,
        currentIndex: currentImages.findIndex((img) => img.file_id === item.file_id),
        visible: true
      };
      previewImage.value = item;
      showPreview.value = true;
      isImageLoading.value = true;
    };
    const nextImage = () => {
      if (previewState.value.currentIndex < previewState.value.images.length - 1) {
        previewState.value.currentIndex++;
        updatePreviewImage();
      }
    };
    const prevImage = () => {
      if (previewState.value.currentIndex > 0) {
        previewState.value.currentIndex--;
        updatePreviewImage();
      }
    };
    const updatePreviewImage = () => {
      const currentImage = previewState.value.images[previewState.value.currentIndex];
      if (currentImage) {
        previewImage.value = currentImage;
        isImageLoading.value = true;
      }
    };
    const closePreview = () => {
      previewState.value.visible = false;
      showPreview.value = false;
      previewImage.value = null;
    };
    const deleteSelected = async () => {
      if (!hasSelection.value) {
        console.log("[删除] 没有选中任何项目");
        return;
      }
      try {
        const fileIds = selectedItems.value.map((item) => item.file_id);
        console.log("[删除] 选中的项目数量:", selectedItems.value.length);
        console.log("[删除] 选中的项目详情:", selectedItems.value);
        console.log("[删除] 准备删除的文件IDs:", fileIds);
        console.log("[删除] fileIds类型:", typeof fileIds, "Array.isArray:", Array.isArray(fileIds));
        const response = await props.api.post("plugin/CloudImg123/delete", { file_ids: fileIds });
        console.log("[删除] API响应:", response);
        if (response.success) {
          await getHistory();
          await getStatistics();
          selectedItems.value = [];
          isDeleteMode.value = false;
          if (response.data) {
            const { deleted, total, failed } = response.data;
            if (failed > 0) {
              showNotificationMessage(`删除完成：成功${deleted}个，失败${failed}个`, "warning");
            } else {
              showNotificationMessage(`成功删除 ${deleted} 条记录`, "success");
            }
          } else {
            showNotificationMessage(response.message || "删除成功", "success");
          }
        } else {
          console.error("[删除] 删除失败:", response.message);
          showNotificationMessage(response.message || "删除失败", "error");
        }
      } catch (error) {
        console.error("删除失败:", error);
        showNotificationMessage("删除过程中发生错误", "error");
      }
    };
    const toggleSelection = (item) => {
      console.log("[勾选] 点击项目:", item.filename, "file_id:", item.file_id);
      const index = selectedItems.value.findIndex((selected) => selected.file_id === item.file_id);
      if (index > -1) {
        selectedItems.value.splice(index, 1);
        console.log("[勾选] 取消选择，当前选中数量:", selectedItems.value.length);
      } else {
        selectedItems.value.push(item);
        console.log("[勾选] 添加选择，当前选中数量:", selectedItems.value.length);
      }
      console.log("[勾选] 当前选中的项目:", selectedItems.value);
    };
    const toggleSelectAll = () => {
      if (selectedItems.value.length === paginatedItems.value.length) {
        selectedItems.value = [];
      } else {
        selectedItems.value = [...paginatedItems.value];
      }
    };
    const getStatistics = async () => {
      try {
        isRefreshing.value = true;
        const response = await props.api.get("plugin/CloudImg123/statistics");
        if (response.success && response.data) {
          statistics.value = {
            totalUploads: response.data.totalUploads || 0,
            totalSize: response.data.totalSize || 0,
            todayUploads: response.data.todayUploads || 0
          };
        } else {
          statistics.value = {
            totalUploads: 0,
            totalSize: 0,
            todayUploads: 0
          };
        }
      } catch (error) {
        console.error("获取统计数据失败:", error);
        const errorMessage = error.response?.data?.message || error.message || "获取统计数据失败";
        console.error(`获取统计数据失败: ${errorMessage}`);
        statistics.value = {
          totalUploads: 0,
          totalSize: 0,
          todayUploads: 0
        };
      } finally {
        isRefreshing.value = false;
      }
    };
    const notifyRefresh = () => {
      emit("action");
      getStatistics();
      if (currentTab.value === "history") {
        getHistory();
      }
    };
    const notifySwitch = () => {
      emit("switch");
    };
    const onSearchChange = () => {
      filterItems();
      nextTick(() => {
        console.log("[搜索调试] 搜索后重新初始化懒加载");
        setupLazyLoading();
        if (typeof resetVirtualScroll === "function") {
          resetVirtualScroll();
        }
        if (typeof recalculateVirtualLayout === "function") {
          recalculateVirtualLayout();
        }
      });
    };
    const setImagesPerRow = (value) => {
      imagesPerRow.value = value;
      localStorage.setItem("cloudimg123_images_per_row", value);
      nextTick(() => {
        recalculateVirtualLayout();
      });
    };
    watch(currentTab, (newVal) => {
      if (newVal === "upload") {
        currentPage.value = 1;
      } else if (newVal === "history") {
        isDeleteMode.value = false;
        selectedItems.value = [];
      }
    });
    watch(currentPage, () => {
      if (currentTab.value === "history") {
        nextTick(() => {
          console.log("[分页调试] 页面切换，重新初始化懒加载");
          setupLazyLoading();
        });
      }
    });
    onMounted(() => {
      const handleClickOutside = (event) => {
        if (showGridSelector.value && !event.target.closest(".grid-control")) {
          showGridSelector.value = false;
        }
      };
      document.addEventListener("click", handleClickOutside);
      onUnmounted(() => {
        document.removeEventListener("click", handleClickOutside);
      });
    });
    const handleKeyDown = (e) => {
      if (!previewState.value.visible) return;
      switch (e.key) {
        case "ArrowLeft":
          e.preventDefault();
          prevImage();
          break;
        case "ArrowRight":
          e.preventDefault();
          nextImage();
          break;
        case "Escape":
          e.preventDefault();
          closePreview();
          break;
      }
    };
    const handleResize = () => {
      window.dispatchEvent(new Event("virtual-scroll-recalculate"));
    };
    onMounted(() => {
      try {
        document._hasThumbnailListener = false;
        const savedImagesPerRow = localStorage.getItem("cloudimg123_images_per_row");
        if (savedImagesPerRow) {
          imagesPerRow.value = parseInt(savedImagesPerRow);
        }
        window.addEventListener("resize", handleResize);
        getStatistics();
        getHistory();
        nextTick(() => {
          setupLazyLoading();
        });
        window.addEventListener("keydown", handleKeyDown);
      } catch (error) {
        console.error("组件初始化失败:", error);
        showNotificationMessage("初始化失败，请检查API配置", "error");
      }
    });
    onUnmounted(() => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("resize", handleResize);
      thumbnailGenerationDebounce.value.forEach((timer) => {
        clearTimeout(timer);
      });
      thumbnailGenerationDebounce.value.clear();
      if (lazyLoadObserver) {
        lazyLoadObserver.destroy();
        lazyLoadObserver = null;
      }
      document.removeEventListener("lazy-load-thumbnail", handleLazyLoadThumbnail);
      document._hasThumbnailListener = false;
    });
    return (_ctx, _cache) => {
      const _component_v_icon = _resolveComponent("v-icon");
      return _openBlock(), _createElementBlock("div", _hoisted_1, [
        _createElementVNode("div", _hoisted_2, [
          _createElementVNode("div", _hoisted_3, [
            _createVNode(_component_v_icon, {
              icon: "mdi-cloud-upload",
              size: "32",
              class: "me-3",
              color: "primary"
            }),
            _cache[45] || (_cache[45] = _createElementVNode("h1", { class: "text-h4 font-weight-bold text-primary" }, "123云盘图床", -1))
          ]),
          _cache[46] || (_cache[46] = _createElementVNode("p", { class: "text-subtitle-1 text-medium-emphasis" }, "配置您的图床服务，享受便捷的图片上传体验", -1))
        ]),
        _createElementVNode("div", _hoisted_4, [
          _createElementVNode("div", {
            class: "stat-item",
            onMouseenter: _cache[0] || (_cache[0] = ($event) => hoveredStat.value = "total"),
            onMouseleave: _cache[1] || (_cache[1] = ($event) => hoveredStat.value = "")
          }, [
            _cache[48] || (_cache[48] = _createElementVNode("span", { class: "stat-label" }, "总上传数", -1)),
            _createElementVNode("div", _hoisted_5, [
              _createElementVNode("span", {
                class: _normalizeClass(["stat-value", { "pulse": hoveredStat.value === "total" }])
              }, _toDisplayString(statistics.value.totalUploads), 3),
              statistics.value.totalUploads > 0 ? (_openBlock(), _createElementBlock("div", _hoisted_6, [..._cache[47] || (_cache[47] = [
                _createElementVNode("svg", {
                  viewBox: "0 0 24 24",
                  width: "14",
                  height: "14"
                }, [
                  _createElementVNode("path", {
                    fill: "currentColor",
                    d: "M21,18H3C2.45,18 2,17.55 2,17V11C2,10.45 2.45,10 3,10H21C21.55,10 22,10.45 22,11V17C22,17.55 21.55,18 21,18M21,8H3C2.45,8 2,7.55 2,7V5C2,4.45 2.45,4 3,4H21C21.55,4 22,4.45 22,5V7C22,7.55 21.55,8 21,8Z"
                  })
                ], -1),
                _createElementVNode("span", null, "累计上传记录", -1)
              ])])) : _createCommentVNode("", true)
            ])
          ], 32),
          _createElementVNode("div", {
            class: "stat-item",
            onMouseenter: _cache[2] || (_cache[2] = ($event) => hoveredStat.value = "size"),
            onMouseleave: _cache[3] || (_cache[3] = ($event) => hoveredStat.value = "")
          }, [
            _cache[50] || (_cache[50] = _createElementVNode("span", { class: "stat-label" }, "总大小", -1)),
            _createElementVNode("div", _hoisted_7, [
              _createElementVNode("span", {
                class: _normalizeClass(["stat-value", { "pulse": hoveredStat.value === "size" }])
              }, _toDisplayString(_unref(formatFileSize)(statistics.value.totalSize)), 3),
              statistics.value.totalSize > 0 ? (_openBlock(), _createElementBlock("div", _hoisted_8, [..._cache[49] || (_cache[49] = [
                _createElementVNode("svg", {
                  viewBox: "0 0 24 24",
                  width: "14",
                  height: "14"
                }, [
                  _createElementVNode("path", {
                    fill: "currentColor",
                    d: "M12,3L2,12H5V20H19V12H22L12,3M12,8.75A2.25,2.25 0 0,1 14.25,11A2.25,2.25 0 0,1 12,13.25A2.25,2.25 0 0,1 9.75,11A2.25,2.25 0 0,1 12,8.75M12,15C13.5,15 16.5,15.75 16.5,17.25V18H7.5V17.25C7.5,15.75 10.5,15 12,15Z"
                  })
                ], -1),
                _createElementVNode("span", null, "存储空间占用", -1)
              ])])) : _createCommentVNode("", true)
            ])
          ], 32),
          _createElementVNode("div", {
            class: "stat-item",
            onMouseenter: _cache[4] || (_cache[4] = ($event) => hoveredStat.value = "today"),
            onMouseleave: _cache[5] || (_cache[5] = ($event) => hoveredStat.value = "")
          }, [
            _cache[52] || (_cache[52] = _createElementVNode("span", { class: "stat-label" }, "今日上传", -1)),
            _createElementVNode("div", _hoisted_9, [
              _createElementVNode("span", {
                class: _normalizeClass(["stat-value", { "pulse": hoveredStat.value === "today" }])
              }, _toDisplayString(statistics.value.todayUploads), 3),
              statistics.value.todayUploads > 0 ? (_openBlock(), _createElementBlock("div", _hoisted_10, [..._cache[51] || (_cache[51] = [
                _createElementVNode("svg", {
                  viewBox: "0 0 24 24",
                  width: "14",
                  height: "14"
                }, [
                  _createElementVNode("path", {
                    fill: "currentColor",
                    d: "M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z"
                  })
                ], -1),
                _createElementVNode("span", null, "今日新增上传", -1)
              ])])) : _createCommentVNode("", true)
            ])
          ], 32),
          _createElementVNode("div", _hoisted_11, [
            _createElementVNode("button", {
              class: _normalizeClass(["icon-btn refresh-btn", { "active": isRefreshing.value }]),
              onClick: notifyRefresh,
              title: "刷新数据"
            }, [
              (_openBlock(), _createElementBlock("svg", {
                viewBox: "0 0 24 24",
                width: "18",
                height: "18",
                class: _normalizeClass({ "rotating": isRefreshing.value })
              }, [..._cache[53] || (_cache[53] = [
                _createElementVNode("path", {
                  fill: "currentColor",
                  d: "M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z"
                }, null, -1)
              ])], 2))
            ], 2),
            _createElementVNode("button", {
              class: "icon-btn config-btn",
              onClick: notifySwitch,
              title: "插件配置",
              onMouseenter: _cache[6] || (_cache[6] = ($event) => showConfigTip.value = true),
              onMouseleave: _cache[7] || (_cache[7] = ($event) => showConfigTip.value = false)
            }, [
              _cache[54] || (_cache[54] = _createElementVNode("svg", {
                viewBox: "0 0 24 24",
                width: "18",
                height: "18"
              }, [
                _createElementVNode("path", {
                  fill: "currentColor",
                  d: "M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"
                })
              ], -1)),
              showConfigTip.value ? (_openBlock(), _createElementBlock("div", _hoisted_12, "进入插件设置")) : _createCommentVNode("", true)
            ], 32)
          ])
        ]),
        _createElementVNode("div", _hoisted_13, [
          _createElementVNode("div", _hoisted_14, [
            _createElementVNode("button", {
              class: _normalizeClass(["tab-btn", { active: currentTab.value === "upload" }]),
              onClick: _cache[8] || (_cache[8] = ($event) => currentTab.value = "upload"),
              onMouseenter: _cache[9] || (_cache[9] = ($event) => tabHover.value = "upload"),
              onMouseleave: _cache[10] || (_cache[10] = ($event) => tabHover.value = "")
            }, [
              _cache[55] || (_cache[55] = _createElementVNode("svg", {
                viewBox: "0 0 24 24",
                width: "16",
                height: "16"
              }, [
                _createElementVNode("path", {
                  fill: "currentColor",
                  d: "M9,16V10H5L12,3L19,10H15V16H9M5,20V18H19V20H5Z"
                })
              ], -1)),
              _cache[56] || (_cache[56] = _createElementVNode("span", null, "图片上传", -1)),
              _createElementVNode("div", {
                class: _normalizeClass(["tab-indicator", { "show": currentTab.value === "upload" || tabHover.value === "upload" }])
              }, null, 2)
            ], 34),
            _createElementVNode("button", {
              class: _normalizeClass(["tab-btn", { active: currentTab.value === "history" }]),
              onClick: _cache[11] || (_cache[11] = ($event) => {
                currentTab.value = "history";
                getHistory();
              }),
              onMouseenter: _cache[12] || (_cache[12] = ($event) => tabHover.value = "history"),
              onMouseleave: _cache[13] || (_cache[13] = ($event) => tabHover.value = "")
            }, [
              _cache[57] || (_cache[57] = _createElementVNode("svg", {
                viewBox: "0 0 24 24",
                width: "16",
                height: "16"
              }, [
                _createElementVNode("path", {
                  fill: "currentColor",
                  d: "M13.5,8H12V13L16.28,15.54L17,14.33L13.5,12.25V8M13,3A9,9 0 0,0 4,12H1L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3"
                })
              ], -1)),
              _cache[58] || (_cache[58] = _createElementVNode("span", null, "历史记录", -1)),
              _createElementVNode("div", {
                class: _normalizeClass(["tab-indicator", { "show": currentTab.value === "history" || tabHover.value === "history" }])
              }, null, 2)
            ], 34)
          ]),
          currentTab.value === "upload" ? (_openBlock(), _createElementBlock("div", _hoisted_15, [
            _createElementVNode("div", {
              class: _normalizeClass(["upload-dropzone", {
                "drag-over": isDragOver.value,
                "uploading": isUploading.value,
                "hover": !isUploading.value && !isDragOver.value
              }]),
              onDrop: handleDrop,
              onDragover: handleDragOver,
              onDragleave: handleDragLeave,
              onClick: _cache[16] || (_cache[16] = ($event) => _ctx.$refs.fileInput?.click())
            }, [
              _createElementVNode("input", {
                ref: "fileInput",
                type: "file",
                multiple: "",
                accept: "image/*",
                onChange: handleFileSelect,
                style: { "display": "none" }
              }, null, 544),
              _createElementVNode("div", _hoisted_16, [
                isUploading.value ? (_openBlock(), _createElementBlock("div", _hoisted_17, [
                  _cache[60] || (_cache[60] = _createElementVNode("div", { class: "upload-spinner" }, null, -1)),
                  _cache[61] || (_cache[61] = _createElementVNode("p", { class: "upload-text" }, "正在上传中...", -1)),
                  _createElementVNode("div", _hoisted_18, [
                    _createElementVNode("div", {
                      class: _normalizeClass(["progress-fill", { "animated": uploadProgress.value > 0 }]),
                      style: _normalizeStyle({ width: uploadProgress.value + "%" })
                    }, null, 6)
                  ]),
                  _createElementVNode("div", _hoisted_19, [
                    _createElementVNode("p", _hoisted_20, _toDisplayString(uploadProgress.value) + "% (" + _toDisplayString(uploadResults.value.length + uploadErrors.value.length) + "/" + _toDisplayString(totalFiles.value) + ")", 1),
                    uploadTasks.value.length > 0 ? (_openBlock(), _createElementBlock("button", {
                      key: 0,
                      onClick: _withModifiers(openUploadList, ["stop"]),
                      class: _normalizeClass(["upload-list-btn", { "has-active": activeUploads.value > 0 }])
                    }, [
                      (_openBlock(), _createElementBlock("svg", _hoisted_21, [..._cache[59] || (_cache[59] = [
                        _createElementVNode("path", {
                          fill: "currentColor",
                          d: "M9,16V10H5L12,3L19,10H15V16H9M5,20V18H19V20H5Z"
                        }, null, -1)
                      ])])),
                      _createTextVNode(" 上传任务 (" + _toDisplayString(activeUploads.value) + "/" + _toDisplayString(uploadTasks.value.length) + ") ", 1),
                      activeUploads.value > 0 ? (_openBlock(), _createElementBlock("span", _hoisted_22)) : _createCommentVNode("", true)
                    ], 2)) : _createCommentVNode("", true)
                  ])
                ])) : (_openBlock(), _createElementBlock("div", _hoisted_23, [
                  _cache[64] || (_cache[64] = _createElementVNode("svg", {
                    class: "upload-icon",
                    viewBox: "0 0 24 24",
                    width: "48",
                    height: "48"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"
                    })
                  ], -1)),
                  _cache[65] || (_cache[65] = _createElementVNode("h3", { class: "dropzone-title" }, "拖拽图片到此处或点击上传", -1)),
                  _cache[66] || (_cache[66] = _createElementVNode("p", { class: "dropzone-subtitle" }, "支持多文件上传，最大100MB", -1)),
                  _createElementVNode("button", {
                    class: "upload-btn",
                    onMouseenter: _cache[14] || (_cache[14] = ($event) => btnHover.value = "upload"),
                    onMouseleave: _cache[15] || (_cache[15] = ($event) => btnHover.value = "")
                  }, [
                    _cache[63] || (_cache[63] = _createElementVNode("span", null, "选择图片", -1)),
                    (_openBlock(), _createElementBlock("svg", {
                      viewBox: "0 0 24 24",
                      width: "16",
                      height: "16",
                      class: _normalizeClass({ "show": btnHover.value === "upload" })
                    }, [..._cache[62] || (_cache[62] = [
                      _createElementVNode("path", {
                        fill: "currentColor",
                        d: "M20,11H7.83L13.42,5.41L12,4L4,12L12,20L13.41,18.59L7.83,13H20V11Z"
                      }, null, -1)
                    ])], 2))
                  ], 32)
                ]))
              ])
            ], 34),
            uploadResults.value.length > 0 || uploadErrors.value.length > 0 ? (_openBlock(), _createElementBlock("div", {
              key: 0,
              class: _normalizeClass(["upload-results", { "show": uploadResults.value.length > 0 || uploadErrors.value.length > 0 }])
            }, [
              _createElementVNode("div", { class: "results-header" }, [
                _cache[68] || (_cache[68] = _createElementVNode("h4", null, "上传结果", -1)),
                _createElementVNode("button", {
                  class: "clear-results",
                  onClick: clearResults,
                  title: "清空结果"
                }, [..._cache[67] || (_cache[67] = [
                  _createElementVNode("svg", {
                    viewBox: "0 0 24 24",
                    width: "16",
                    height: "16"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"
                    })
                  ], -1)
                ])])
              ]),
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(uploadResults.value, (result) => {
                return _openBlock(), _createElementBlock("div", {
                  key: result.filename,
                  class: _normalizeClass(["result-item success", { "show": uploadResults.value.length > 0 }])
                }, [
                  _createElementVNode("div", _hoisted_24, [
                    _cache[69] || (_cache[69] = _createElementVNode("svg", {
                      class: "result-icon",
                      viewBox: "0 0 24 24",
                      width: "16",
                      height: "16"
                    }, [
                      _createElementVNode("path", {
                        fill: "currentColor",
                        d: "M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M11,16.5L18,9.5L16.59,8.09L11,13.67L7.91,10.59L6.5,12L11,16.5Z"
                      })
                    ], -1)),
                    _createElementVNode("span", _hoisted_25, _toDisplayString(result.filename), 1)
                  ]),
                  _createElementVNode("div", _hoisted_26, [
                    _createElementVNode("div", _hoisted_27, [
                      _createElementVNode("div", _hoisted_28, [
                        _createElementVNode("img", {
                          src: extractImageUrl(result.links.url),
                          alt: result.filename,
                          class: "result-thumbnail",
                          onError: _cache[17] || (_cache[17] = ($event) => handleThumbnailError($event))
                        }, null, 40, _hoisted_29)
                      ])
                    ]),
                    _createElementVNode("div", _hoisted_30, [
                      _createElementVNode("div", _hoisted_31, [
                        _createElementVNode("div", _hoisted_32, [
                          _cache[70] || (_cache[70] = _createElementVNode("label", null, "URL", -1)),
                          _createElementVNode("div", _hoisted_33, [
                            _createElementVNode("input", {
                              readonly: "",
                              value: result.links.url,
                              class: "link-input",
                              onClick: _cache[18] || (_cache[18] = ($event) => selectAll($event))
                            }, null, 8, _hoisted_34),
                            _createElementVNode("button", {
                              onClick: ($event) => copyLink(result.links.url, "URL"),
                              class: _normalizeClass(["copy-btn", { "copied": copiedLink.value === result.links.url }])
                            }, _toDisplayString(copiedLink.value === result.links.url ? "已复制" : "复制"), 11, _hoisted_35)
                          ])
                        ]),
                        _createElementVNode("div", _hoisted_36, [
                          _cache[71] || (_cache[71] = _createElementVNode("label", null, "HTML", -1)),
                          _createElementVNode("div", _hoisted_37, [
                            _createElementVNode("input", {
                              readonly: "",
                              value: result.links.html,
                              class: "link-input",
                              onClick: _cache[19] || (_cache[19] = ($event) => selectAll($event))
                            }, null, 8, _hoisted_38),
                            _createElementVNode("button", {
                              onClick: ($event) => copyLink(result.links.html, "HTML"),
                              class: _normalizeClass(["copy-btn", { "copied": copiedLink.value === result.links.html }])
                            }, _toDisplayString(copiedLink.value === result.links.html ? "已复制" : "复制"), 11, _hoisted_39)
                          ])
                        ])
                      ]),
                      _createElementVNode("div", _hoisted_40, [
                        _createElementVNode("div", _hoisted_41, [
                          _cache[72] || (_cache[72] = _createElementVNode("label", null, "Markdown", -1)),
                          _createElementVNode("div", _hoisted_42, [
                            _createElementVNode("input", {
                              readonly: "",
                              value: result.links.markdown,
                              class: "link-input",
                              onClick: _cache[20] || (_cache[20] = ($event) => selectAll($event))
                            }, null, 8, _hoisted_43),
                            _createElementVNode("button", {
                              onClick: ($event) => copyLink(result.links.markdown, "Markdown"),
                              class: _normalizeClass(["copy-btn", { "copied": copiedLink.value === result.links.markdown }])
                            }, _toDisplayString(copiedLink.value === result.links.markdown ? "已复制" : "复制"), 11, _hoisted_44)
                          ])
                        ]),
                        _createElementVNode("div", _hoisted_45, [
                          _cache[73] || (_cache[73] = _createElementVNode("label", null, "BBCode", -1)),
                          _createElementVNode("div", _hoisted_46, [
                            _createElementVNode("input", {
                              readonly: "",
                              value: result.links.bbcode,
                              class: "link-input",
                              onClick: _cache[21] || (_cache[21] = ($event) => selectAll($event))
                            }, null, 8, _hoisted_47),
                            _createElementVNode("button", {
                              onClick: ($event) => copyLink(result.links.bbcode, "BBCode"),
                              class: _normalizeClass(["copy-btn", { "copied": copiedLink.value === result.links.bbcode }])
                            }, _toDisplayString(copiedLink.value === result.links.bbcode ? "已复制" : "复制"), 11, _hoisted_48)
                          ])
                        ])
                      ])
                    ])
                  ])
                ], 2);
              }), 128)),
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(uploadErrors.value, (error) => {
                return _openBlock(), _createElementBlock("div", {
                  key: error,
                  class: _normalizeClass(["result-item error", { "show": uploadErrors.value.length > 0 }])
                }, [
                  _createElementVNode("div", _hoisted_49, [
                    _cache[74] || (_cache[74] = _createElementVNode("svg", {
                      class: "result-icon",
                      viewBox: "0 0 24 24",
                      width: "16",
                      height: "16"
                    }, [
                      _createElementVNode("path", {
                        fill: "currentColor",
                        d: "M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,7A5,5 0 0,0 7,12A5,5 0 0,0 12,17A5,5 0 0,0 17,12A5,5 0 0,0 12,7M12,9A3,3 0 0,1 15,12A3,3 0 0,1 12,15A3,3 0 0,1 9,12A3,3 0 0,1 12,9Z"
                      })
                    ], -1)),
                    _createElementVNode("span", _hoisted_50, _toDisplayString(error), 1)
                  ])
                ], 2);
              }), 128))
            ], 2)) : _createCommentVNode("", true)
          ])) : _createCommentVNode("", true),
          currentTab.value === "history" ? (_openBlock(), _createElementBlock("div", _hoisted_51, [
            _createElementVNode("div", _hoisted_52, [
              _createElementVNode("div", _hoisted_53, [
                _createElementVNode("div", _hoisted_54, [
                  _cache[76] || (_cache[76] = _createElementVNode("svg", {
                    class: "search-icon",
                    viewBox: "0 0 24 24",
                    width: "20",
                    height: "20"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"
                    })
                  ], -1)),
                  _withDirectives(_createElementVNode("input", {
                    "onUpdate:modelValue": _cache[22] || (_cache[22] = ($event) => searchQuery.value = $event),
                    onInput: onSearchChange,
                    type: "text",
                    class: "search-input",
                    placeholder: "搜索图片文件名..."
                  }, null, 544), [
                    [_vModelText, searchQuery.value]
                  ]),
                  searchQuery.value ? (_openBlock(), _createElementBlock("button", {
                    key: 0,
                    onClick: _cache[23] || (_cache[23] = ($event) => {
                      searchQuery.value = "";
                      onSearchChange();
                    }),
                    class: "clear-search-btn",
                    title: "清除搜索"
                  }, [..._cache[75] || (_cache[75] = [
                    _createElementVNode("svg", {
                      viewBox: "0 0 24 24",
                      width: "16",
                      height: "16"
                    }, [
                      _createElementVNode("path", {
                        fill: "currentColor",
                        d: "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"
                      })
                    ], -1)
                  ])])) : _createCommentVNode("", true)
                ])
              ]),
              _createElementVNode("div", _hoisted_55, [
                _createElementVNode("div", _hoisted_56, [
                  _createElementVNode("div", {
                    class: "grid-icon-btn",
                    onClick: _cache[24] || (_cache[24] = ($event) => showGridSelector.value = !showGridSelector.value),
                    title: "调整每行显示数量"
                  }, [..._cache[77] || (_cache[77] = [
                    _createElementVNode("svg", {
                      class: "grid-icon",
                      viewBox: "0 0 24 24",
                      width: "18",
                      height: "18"
                    }, [
                      _createElementVNode("path", {
                        fill: "currentColor",
                        d: "M4,4H8V8H4V4M10,4H14V8H10V4M16,4H20V8H16V4M4,10H8V14H4V10M10,10H14V14H10V10M16,10H20V14H16V10M4,16H8V20H4V16M10,16H14V20H10V16M16,16H20V20H16V16Z"
                      })
                    ], -1)
                  ])]),
                  showGridSelector.value ? (_openBlock(), _createElementBlock("div", {
                    key: 0,
                    class: "grid-selector-popup",
                    onMousedown: _cache[25] || (_cache[25] = _withModifiers(() => {
                    }, ["stop"])),
                    onTouchstart: _cache[26] || (_cache[26] = _withModifiers(() => {
                    }, ["stop"]))
                  }, [
                    _createElementVNode("div", _hoisted_57, [
                      (_openBlock(), _createElementBlock(_Fragment, null, _renderList(gridOptions, (option) => {
                        return _createElementVNode("button", {
                          key: option,
                          class: _normalizeClass(["grid-option-btn", { "active": imagesPerRow.value === option }]),
                          onClick: ($event) => selectGridOption(option)
                        }, _toDisplayString(option), 11, _hoisted_58);
                      }), 64))
                    ])
                  ], 32)) : _createCommentVNode("", true)
                ]),
                isDeleteMode.value ? (_openBlock(), _createElementBlock("button", {
                  key: 0,
                  onClick: deleteSelected,
                  disabled: !hasSelection.value,
                  class: _normalizeClass(["action-btn delete-btn", { "disabled": !hasSelection.value }])
                }, " 删除选中 ", 10, _hoisted_59)) : _createCommentVNode("", true),
                _createElementVNode("button", {
                  onClick: _cache[27] || (_cache[27] = ($event) => isDeleteMode.value = !isDeleteMode.value),
                  class: _normalizeClass(["action-btn toggle-btn", { "active": isDeleteMode.value }])
                }, _toDisplayString(isDeleteMode.value ? "取消选择" : "批量删除"), 3)
              ])
            ]),
            isLoading.value ? (_openBlock(), _createElementBlock("div", _hoisted_60, [..._cache[78] || (_cache[78] = [
              _createElementVNode("div", { class: "spinner" }, null, -1),
              _createElementVNode("p", null, "加载历史记录中...", -1)
            ])])) : filteredItems.value.length === 0 ? (_openBlock(), _createElementBlock("div", _hoisted_61, [
              _cache[79] || (_cache[79] = _createElementVNode("svg", {
                class: "empty-icon",
                viewBox: "0 0 24 24",
                width: "64",
                height: "64"
              }, [
                _createElementVNode("path", {
                  fill: "currentColor",
                  d: "M21,17H7V3A1,1 0 0,1 8,2H20A1,1 0 0,1 21,3V17M17,10V12H11V10H17M17,8V6H11V8H17M7,19A3,3 0 0,0 10,22H22V20H10A1,1 0 0,1 9,19H22V17H7V19M17,14V16H11V14H17Z"
                })
              ], -1)),
              _createElementVNode("h3", null, _toDisplayString(searchQuery.value ? "未找到匹配的记录" : "暂无上传历史"), 1),
              _createElementVNode("p", null, _toDisplayString(searchQuery.value ? "尝试修改搜索条件" : "开始上传图片后，这里会显示历史记录"), 1),
              !searchQuery.value ? (_openBlock(), _createElementBlock("button", {
                key: 0,
                class: "primary-btn",
                onClick: _cache[28] || (_cache[28] = ($event) => currentTab.value = "upload")
              }, " 去上传图片 ")) : _createCommentVNode("", true)
            ])) : (_openBlock(), _createElementBlock("div", _hoisted_62, [
              isDeleteMode.value ? (_openBlock(), _createElementBlock("div", _hoisted_63, [
                _createElementVNode("label", _hoisted_64, [
                  _createElementVNode("input", {
                    type: "checkbox",
                    checked: selectedItems.value.length === paginatedItems.value.length && paginatedItems.value.length > 0,
                    onChange: toggleSelectAll,
                    indeterminate: selectedItems.value.length > 0 && selectedItems.value.length < paginatedItems.value.length
                  }, null, 40, _hoisted_65),
                  _createTextVNode(" 全选当前页 (" + _toDisplayString(selectedItems.value.length) + "/" + _toDisplayString(paginatedItems.value.length) + ") ", 1)
                ])
              ])) : _createCommentVNode("", true),
              ENABLE_VIRTUAL_SCROLL.value ? (_openBlock(), _createElementBlock("div", {
                key: 1,
                ref_key: "virtualContainerRef",
                ref: virtualContainerRef,
                style: _normalizeStyle(_unref(virtualContainerStyle)),
                class: "virtual-scroll-container"
              }, [
                _createElementVNode("div", {
                  style: _normalizeStyle(_unref(virtualContentStyle))
                }, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_unref(virtualVisibleItems), (item) => {
                    return _openBlock(), _createElementBlock("div", {
                      key: item.file_id,
                      class: _normalizeClass(["history-card", {
                        "selected": isDeleteMode.value && isSelected(item),
                        "invalid": item.isInvalid
                      }]),
                      style: _normalizeStyle({
                        position: "absolute",
                        top: `${item._virtualTop}px`,
                        left: `${item._virtualLeft}px`,
                        width: "280px"
                      }),
                      onMouseenter: ($event) => cardHover.value = item.file_id,
                      onMouseleave: _cache[29] || (_cache[29] = ($event) => cardHover.value = null)
                    }, [
                      isDeleteMode.value ? (_openBlock(), _createElementBlock("div", _hoisted_67, [
                        _createElementVNode("input", {
                          type: "checkbox",
                          checked: isSelected(item),
                          onChange: ($event) => toggleSelection(item),
                          class: "selection-checkbox"
                        }, null, 40, _hoisted_68)
                      ])) : _createCommentVNode("", true),
                      _createElementVNode("div", {
                        class: "image-preview",
                        onClick: ($event) => previewItem(item)
                      }, [
                        item.isGeneratingThumbnail ? (_openBlock(), _createElementBlock("div", _hoisted_70, [..._cache[80] || (_cache[80] = [
                          _createElementVNode("div", { class: "thumbnail-spinner" }, null, -1),
                          _createElementVNode("span", { class: "thumbnail-generating-text" }, "生成中", -1)
                        ])])) : _createCommentVNode("", true),
                        _createElementVNode("img", {
                          src: getBestImageUrl(item),
                          "data-src": item._lazyActualUrl,
                          "data-lazy-type": item._lazyType,
                          "data-file-id": item.file_id,
                          alt: escapeHtml(item.original_name),
                          onError: ($event) => handleImageError($event, item),
                          onLoad: ($event) => handleImageLoad($event, item),
                          class: _normalizeClass({ "thumbnail": item.has_local_thumbnail, "lazy-image": true })
                        }, null, 42, _hoisted_71),
                        _createElementVNode("div", {
                          class: _normalizeClass(["image-overlay", { "visible": cardHover.value === item.file_id }])
                        }, [
                          _createElementVNode("button", {
                            onClick: _withModifiers(($event) => previewItem(item), ["stop"]),
                            class: "overlay-btn preview-btn"
                          }, [..._cache[81] || (_cache[81] = [
                            _createElementVNode("svg", {
                              viewBox: "0 0 24 24",
                              width: "16",
                              height: "16"
                            }, [
                              _createElementVNode("path", {
                                fill: "currentColor",
                                d: "M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"
                              })
                            ], -1),
                            _createTextVNode(" 预览 ", -1)
                          ])], 8, _hoisted_72),
                          !item.has_local_thumbnail ? (_openBlock(), _createElementBlock("button", {
                            key: 0,
                            onClick: _withModifiers(($event) => generateThumbnail(item.file_id), ["stop"]),
                            class: "overlay-btn generate-btn",
                            title: "生成缩略图"
                          }, [..._cache[82] || (_cache[82] = [
                            _createElementVNode("svg", {
                              viewBox: "0 0 24 24",
                              width: "16",
                              height: "16"
                            }, [
                              _createElementVNode("path", {
                                fill: "currentColor",
                                d: "M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6M12,8A4,4 0 0,0 8,12A4,4 0 0,0 12,16A4,4 0 0,0 16,12A4,4 0 0,0 12,8Z"
                              })
                            ], -1),
                            _createTextVNode(" 生成缩略图 ", -1)
                          ])], 8, _hoisted_73)) : _createCommentVNode("", true)
                        ], 2)
                      ], 8, _hoisted_69),
                      _createElementVNode("div", _hoisted_74, [
                        _createElementVNode("div", {
                          class: "filename",
                          title: escapeHtml(item.original_name)
                        }, _toDisplayString(escapeHtml(item.original_name)), 9, _hoisted_75),
                        _createElementVNode("div", _hoisted_76, [
                          _createElementVNode("span", _hoisted_77, _toDisplayString(_unref(formatFileSize)(item.file_size)), 1),
                          _createElementVNode("span", _hoisted_78, _toDisplayString(_unref(formatTimeAgo)(item.upload_time)), 1)
                        ])
                      ]),
                      _createElementVNode("div", {
                        class: _normalizeClass(["link-actions", { "compact-mode": imagesPerRow.value >= 4 }])
                      }, [
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.url, "URL"), ["prevent"]),
                          class: _normalizeClass(["link-btn url-btn", { "copied": copiedLink.value === item.formats.url }]),
                          title: "复制URL"
                        }, " URL ", 10, _hoisted_79),
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.markdown, "Markdown"), ["prevent"]),
                          class: _normalizeClass(["link-btn md-btn", { "copied": copiedLink.value === item.formats.markdown }]),
                          title: "复制Markdown"
                        }, " MD ", 10, _hoisted_80),
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.html, "HTML"), ["prevent"]),
                          class: _normalizeClass(["link-btn html-btn", { "copied": copiedLink.value === item.formats.html }]),
                          title: "复制HTML"
                        }, " HTML ", 10, _hoisted_81),
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.bbcode, "BBCode"), ["prevent"]),
                          class: _normalizeClass(["link-btn bb-btn", { "copied": copiedLink.value === item.formats.bbcode }]),
                          title: "复制BBCode"
                        }, " BB ", 10, _hoisted_82)
                      ], 2)
                    ], 46, _hoisted_66);
                  }), 128))
                ], 4)
              ], 4)) : (_openBlock(), _createElementBlock("div", {
                key: 2,
                class: "history-grid",
                style: _normalizeStyle(gridStyle.value)
              }, [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(paginatedItems.value, (item) => {
                  return _openBlock(), _createElementBlock("div", {
                    key: item.file_id,
                    class: _normalizeClass(["history-card", {
                      "selected": isDeleteMode.value && isSelected(item),
                      "invalid": item.isInvalid
                    }]),
                    onMouseenter: ($event) => cardHover.value = item.file_id,
                    onMouseleave: _cache[30] || (_cache[30] = ($event) => cardHover.value = null)
                  }, [
                    isDeleteMode.value ? (_openBlock(), _createElementBlock("div", _hoisted_84, [
                      _createElementVNode("input", {
                        type: "checkbox",
                        checked: isSelected(item),
                        onChange: ($event) => toggleSelection(item),
                        class: "selection-checkbox"
                      }, null, 40, _hoisted_85)
                    ])) : _createCommentVNode("", true),
                    _createElementVNode("div", {
                      class: "image-preview",
                      onClick: ($event) => previewItem(item)
                    }, [
                      item.isGeneratingThumbnail ? (_openBlock(), _createElementBlock("div", _hoisted_87, [..._cache[83] || (_cache[83] = [
                        _createElementVNode("div", { class: "thumbnail-spinner" }, null, -1),
                        _createElementVNode("span", { class: "thumbnail-generating-text" }, "生成中", -1)
                      ])])) : _createCommentVNode("", true),
                      _createElementVNode("img", {
                        src: getBestImageUrl(item),
                        "data-src": item._lazyActualUrl,
                        "data-lazy-type": item._lazyType,
                        "data-file-id": item.file_id,
                        alt: escapeHtml(item.original_name),
                        onError: ($event) => handleImageError($event, item),
                        onLoad: ($event) => handleImageLoad($event, item),
                        class: _normalizeClass({ "thumbnail": item.has_local_thumbnail, "lazy-image": true })
                      }, null, 42, _hoisted_88),
                      _createElementVNode("div", {
                        class: _normalizeClass(["image-overlay", { "visible": cardHover.value === item.file_id }])
                      }, [
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => previewItem(item), ["stop"]),
                          class: "overlay-btn preview-btn"
                        }, [..._cache[84] || (_cache[84] = [
                          _createElementVNode("svg", {
                            viewBox: "0 0 24 24",
                            width: "16",
                            height: "16"
                          }, [
                            _createElementVNode("path", {
                              fill: "currentColor",
                              d: "M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"
                            })
                          ], -1),
                          _createTextVNode(" 预览 ", -1)
                        ])], 8, _hoisted_89)
                      ], 2),
                      item.isInvalid ? (_openBlock(), _createElementBlock("div", _hoisted_90, [..._cache[85] || (_cache[85] = [
                        _createElementVNode("svg", {
                          viewBox: "0 0 24 24",
                          width: "14",
                          height: "14"
                        }, [
                          _createElementVNode("path", {
                            fill: "currentColor",
                            d: "M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M13,17H11V15H13V17M13,13H11V7H13V13Z"
                          })
                        ], -1),
                        _createTextVNode(" 失效 ", -1)
                      ])])) : _createCommentVNode("", true)
                    ], 8, _hoisted_86),
                    _createElementVNode("div", _hoisted_91, [
                      _createElementVNode("div", _hoisted_92, [
                        _createElementVNode("h4", {
                          class: "file-name",
                          title: escapeHtml(item.original_name)
                        }, _toDisplayString(escapeHtml(item.original_name)), 9, _hoisted_93),
                        _createElementVNode("div", _hoisted_94, [
                          _createElementVNode("span", _hoisted_95, _toDisplayString(_unref(formatFileSize)(item.file_size)), 1),
                          _createElementVNode("span", _hoisted_96, _toDisplayString(_unref(formatTimeAgo)(item.upload_time)), 1)
                        ])
                      ]),
                      _createElementVNode("div", {
                        class: _normalizeClass(["link-actions", { "compact-mode": imagesPerRow.value >= 4 }])
                      }, [
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.url, "URL"), ["prevent"]),
                          class: _normalizeClass(["link-btn url-btn", { "copied": copiedLink.value === item.formats.url }]),
                          title: "复制URL"
                        }, " URL ", 10, _hoisted_97),
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.markdown, "Markdown"), ["prevent"]),
                          class: _normalizeClass(["link-btn md-btn", { "copied": copiedLink.value === item.formats.markdown }]),
                          title: "复制Markdown"
                        }, " MD ", 10, _hoisted_98),
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.html, "HTML"), ["prevent"]),
                          class: _normalizeClass(["link-btn html-btn", { "copied": copiedLink.value === item.formats.html }]),
                          title: "复制HTML"
                        }, " HTML ", 10, _hoisted_99),
                        _createElementVNode("button", {
                          onClick: _withModifiers(($event) => copyLink(item.formats.bbcode, "BBCode"), ["prevent"]),
                          class: _normalizeClass(["link-btn bb-btn", { "copied": copiedLink.value === item.formats.bbcode }]),
                          title: "复制BBCode"
                        }, " BB ", 10, _hoisted_100)
                      ], 2)
                    ])
                  ], 42, _hoisted_83);
                }), 128))
              ], 4)),
              totalPages.value > 1 ? (_openBlock(), _createElementBlock("div", _hoisted_101, [
                _createElementVNode("button", {
                  onClick: _cache[31] || (_cache[31] = ($event) => currentPage.value = Math.max(1, currentPage.value - 1)),
                  disabled: currentPage.value === 1,
                  class: _normalizeClass(["page-btn prev-btn", { "disabled": currentPage.value === 1 }])
                }, [..._cache[86] || (_cache[86] = [
                  _createElementVNode("svg", {
                    viewBox: "0 0 24 24",
                    width: "16",
                    height: "16"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"
                    })
                  ], -1),
                  _createTextVNode(" 上一页 ", -1)
                ])], 10, _hoisted_102),
                _createElementVNode("span", _hoisted_103, " 第 " + _toDisplayString(currentPage.value) + " 页，共 " + _toDisplayString(totalPages.value) + " 页 ", 1),
                _createElementVNode("button", {
                  onClick: _cache[32] || (_cache[32] = ($event) => currentPage.value = Math.min(totalPages.value, currentPage.value + 1)),
                  disabled: currentPage.value === totalPages.value,
                  class: _normalizeClass(["page-btn next-btn", { "disabled": currentPage.value === totalPages.value }])
                }, [..._cache[87] || (_cache[87] = [
                  _createTextVNode(" 下一页 ", -1),
                  _createElementVNode("svg", {
                    viewBox: "0 0 24 24",
                    width: "16",
                    height: "16"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"
                    })
                  ], -1)
                ])], 10, _hoisted_104)
              ])) : _createCommentVNode("", true)
            ]))
          ])) : _createCommentVNode("", true)
        ]),
        showPreview.value && previewImage.value ? (_openBlock(), _createElementBlock("div", {
          key: 0,
          class: _normalizeClass(["modal-overlay", { "visible": showPreview.value }]),
          onClick: _cache[43] || (_cache[43] = ($event) => showPreview.value = false)
        }, [
          _createElementVNode("div", {
            class: "modal-content preview-modal",
            onClick: _cache[42] || (_cache[42] = _withModifiers(() => {
            }, ["stop"]))
          }, [
            _createElementVNode("div", _hoisted_105, [
              _createElementVNode("div", _hoisted_106, [
                _createElementVNode("div", _hoisted_107, [
                  _createElementVNode("h3", null, _toDisplayString(escapeHtml(previewImage.value.original_name)), 1),
                  _createElementVNode("div", _hoisted_108, [
                    _createElementVNode("span", null, _toDisplayString(_unref(formatFileSize)(previewImage.value.file_size)), 1),
                    _cache[88] || (_cache[88] = _createElementVNode("span", null, "•", -1)),
                    _createElementVNode("span", null, _toDisplayString(_unref(formatDateTime)(previewImage.value.upload_time)), 1)
                  ]),
                  previewState.value.images.length > 1 ? (_openBlock(), _createElementBlock("div", _hoisted_109, [
                    _createElementVNode("span", null, _toDisplayString(previewState.value.currentIndex + 1) + " / " + _toDisplayString(previewState.value.images.length), 1)
                  ])) : _createCommentVNode("", true)
                ])
              ]),
              _createElementVNode("div", _hoisted_110, [
                _createElementVNode("button", {
                  class: "download-btn",
                  onClick: _cache[33] || (_cache[33] = ($event) => downloadImage(previewImage.value.download_url, previewImage.value.original_name)),
                  disabled: previewImage.value.isInvalid,
                  title: "下载图片"
                }, [..._cache[89] || (_cache[89] = [
                  _createElementVNode("svg", {
                    viewBox: "0 0 24 24",
                    width: "16",
                    height: "16"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M19,9H15V3H9V9H5L12,16L19,9M5,18V20H19V18H5Z"
                    })
                  ], -1)
                ])], 8, _hoisted_111),
                _createElementVNode("button", {
                  onClick: closePreview,
                  class: "close-btn",
                  title: "关闭"
                }, [..._cache[90] || (_cache[90] = [
                  _createElementVNode("svg", {
                    viewBox: "0 0 24 24",
                    width: "20",
                    height: "20"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"
                    })
                  ], -1)
                ])])
              ])
            ]),
            _createElementVNode("div", _hoisted_112, [
              isImageLoading.value ? (_openBlock(), _createElementBlock("div", _hoisted_113, [..._cache[91] || (_cache[91] = [
                _createElementVNode("div", { class: "spinner" }, null, -1)
              ])])) : _createCommentVNode("", true),
              previewState.value.images.length > 1 && previewState.value.currentIndex > 0 ? (_openBlock(), _createElementBlock("button", {
                key: 1,
                onClick: prevImage,
                class: "nav-btn prev-btn",
                title: "上一张 (←)"
              }, [..._cache[92] || (_cache[92] = [
                _createElementVNode("svg", {
                  viewBox: "0 0 24 24",
                  width: "24",
                  height: "24"
                }, [
                  _createElementVNode("path", {
                    fill: "currentColor",
                    d: "M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"
                  })
                ], -1)
              ])])) : _createCommentVNode("", true),
              previewState.value.images.length > 1 && previewState.value.currentIndex < previewState.value.images.length - 1 ? (_openBlock(), _createElementBlock("button", {
                key: 2,
                onClick: nextImage,
                class: "nav-btn next-btn",
                title: "下一张 (→)"
              }, [..._cache[93] || (_cache[93] = [
                _createElementVNode("svg", {
                  viewBox: "0 0 24 24",
                  width: "24",
                  height: "24"
                }, [
                  _createElementVNode("path", {
                    fill: "currentColor",
                    d: "M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"
                  })
                ], -1)
              ])])) : _createCommentVNode("", true),
              !previewImage.value.isInvalid ? (_openBlock(), _createElementBlock("img", {
                key: 3,
                src: previewImage.value.download_url,
                alt: escapeHtml(previewImage.value.original_name),
                onError: handleModalImageError,
                onLoad: handleModalImageLoad,
                class: "preview-image",
                loading: "lazy"
              }, null, 40, _hoisted_114)) : _createCommentVNode("", true),
              previewImage.value.isInvalid ? (_openBlock(), _createElementBlock("div", _hoisted_115, [..._cache[94] || (_cache[94] = [
                _createElementVNode("svg", {
                  viewBox: "0 0 24 24",
                  width: "48",
                  height: "48"
                }, [
                  _createElementVNode("path", {
                    fill: "currentColor",
                    d: "M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M13,17H11V15H13V17M13,13H11V7H13V13Z"
                  })
                ], -1),
                _createElementVNode("p", null, "图片已失效或无法访问", -1)
              ])])) : _createCommentVNode("", true)
            ]),
            _createElementVNode("div", _hoisted_116, [
              _createElementVNode("div", _hoisted_117, [
                _cache[95] || (_cache[95] = _createElementVNode("label", null, "URL", -1)),
                _createElementVNode("div", _hoisted_118, [
                  _createElementVNode("input", {
                    readonly: "",
                    value: previewImage.value.formats.url,
                    class: "syntax-input",
                    onClick: _cache[34] || (_cache[34] = ($event) => selectAll($event))
                  }, null, 8, _hoisted_119),
                  _createElementVNode("button", {
                    onClick: _cache[35] || (_cache[35] = ($event) => copyLink(previewImage.value.formats.url, "URL")),
                    class: _normalizeClass(["syntax-copy-btn", { "copied": copiedLink.value === previewImage.value.formats.url }]),
                    title: "复制URL"
                  }, _toDisplayString(copiedLink.value === previewImage.value.formats.url ? "已复制" : "复制"), 3)
                ])
              ]),
              _createElementVNode("div", _hoisted_120, [
                _cache[96] || (_cache[96] = _createElementVNode("label", null, "HTML", -1)),
                _createElementVNode("div", _hoisted_121, [
                  _createElementVNode("input", {
                    readonly: "",
                    value: previewImage.value.formats.html,
                    class: "syntax-input",
                    onClick: _cache[36] || (_cache[36] = ($event) => selectAll($event))
                  }, null, 8, _hoisted_122),
                  _createElementVNode("button", {
                    onClick: _cache[37] || (_cache[37] = ($event) => copyLink(previewImage.value.formats.html, "HTML")),
                    class: _normalizeClass(["syntax-copy-btn", { "copied": copiedLink.value === previewImage.value.formats.html }]),
                    title: "复制HTML"
                  }, _toDisplayString(copiedLink.value === previewImage.value.formats.html ? "已复制" : "复制"), 3)
                ])
              ]),
              _createElementVNode("div", _hoisted_123, [
                _cache[97] || (_cache[97] = _createElementVNode("label", null, "Markdown", -1)),
                _createElementVNode("div", _hoisted_124, [
                  _createElementVNode("input", {
                    readonly: "",
                    value: previewImage.value.formats.markdown,
                    class: "syntax-input",
                    onClick: _cache[38] || (_cache[38] = ($event) => selectAll($event))
                  }, null, 8, _hoisted_125),
                  _createElementVNode("button", {
                    onClick: _cache[39] || (_cache[39] = ($event) => copyLink(previewImage.value.formats.markdown, "Markdown")),
                    class: _normalizeClass(["syntax-copy-btn", { "copied": copiedLink.value === previewImage.value.formats.markdown }]),
                    title: "复制Markdown"
                  }, _toDisplayString(copiedLink.value === previewImage.value.formats.markdown ? "已复制" : "复制"), 3)
                ])
              ]),
              _createElementVNode("div", _hoisted_126, [
                _cache[98] || (_cache[98] = _createElementVNode("label", null, "BBCode", -1)),
                _createElementVNode("div", _hoisted_127, [
                  _createElementVNode("input", {
                    readonly: "",
                    value: previewImage.value.formats.bbcode,
                    class: "syntax-input",
                    onClick: _cache[40] || (_cache[40] = ($event) => selectAll($event))
                  }, null, 8, _hoisted_128),
                  _createElementVNode("button", {
                    onClick: _cache[41] || (_cache[41] = ($event) => copyLink(previewImage.value.formats.bbcode, "BBCode")),
                    class: _normalizeClass(["syntax-copy-btn", { "copied": copiedLink.value === previewImage.value.formats.bbcode }]),
                    title: "复制BBCode"
                  }, _toDisplayString(copiedLink.value === previewImage.value.formats.bbcode ? "已复制" : "复制"), 3)
                ])
              ])
            ])
          ])
        ], 2)) : _createCommentVNode("", true),
        showUploadList.value ? (_openBlock(), _createElementBlock("div", {
          key: 1,
          class: _normalizeClass(["modal-overlay", { "visible": showUploadList.value }]),
          onClick: closeUploadList
        }, [
          _createElementVNode("div", {
            class: "modal-content upload-list-modal",
            onClick: _cache[44] || (_cache[44] = _withModifiers(() => {
            }, ["stop"]))
          }, [
            _createElementVNode("div", _hoisted_129, [
              _createElementVNode("div", _hoisted_130, [
                _cache[99] || (_cache[99] = _createElementVNode("h3", null, "上传任务列表", -1)),
                _createElementVNode("span", _hoisted_131, "(" + _toDisplayString(activeUploads.value) + "/" + _toDisplayString(uploadTasks.value.length) + ")", 1)
              ]),
              _createElementVNode("div", _hoisted_132, [
                uploadTasks.value.length > 0 ? (_openBlock(), _createElementBlock("button", {
                  key: 0,
                  onClick: cancelAllUploads,
                  class: "cancel-all-btn",
                  disabled: activeUploads.value === 0
                }, [
                  (_openBlock(), _createElementBlock("svg", _hoisted_134, [..._cache[100] || (_cache[100] = [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"
                    }, null, -1)
                  ])])),
                  _cache[101] || (_cache[101] = _createTextVNode(" 取消全部 ", -1))
                ], 8, _hoisted_133)) : _createCommentVNode("", true),
                _createElementVNode("button", {
                  onClick: closeUploadList,
                  class: "close-btn"
                }, [..._cache[102] || (_cache[102] = [
                  _createElementVNode("svg", {
                    viewBox: "0 0 24 24",
                    width: "20",
                    height: "20"
                  }, [
                    _createElementVNode("path", {
                      fill: "currentColor",
                      d: "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"
                    })
                  ], -1)
                ])])
              ])
            ]),
            _createElementVNode("div", _hoisted_135, [
              uploadTasks.value.length === 0 ? (_openBlock(), _createElementBlock("div", _hoisted_136, [..._cache[103] || (_cache[103] = [
                _createElementVNode("svg", {
                  viewBox: "0 0 24 24",
                  width: "48",
                  height: "48"
                }, [
                  _createElementVNode("path", {
                    fill: "currentColor",
                    d: "M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"
                  })
                ], -1),
                _createElementVNode("p", null, "暂无上传任务", -1)
              ])])) : (_openBlock(), _createElementBlock("div", _hoisted_137, [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(uploadTasks.value, (task) => {
                  return _openBlock(), _createElementBlock("div", {
                    key: task.id,
                    class: _normalizeClass(["upload-task-item", {
                      "uploading": task.status === "uploading",
                      "completed": task.status === "completed",
                      "error": task.status === "error",
                      "cancelled": task.status === "cancelled"
                    }])
                  }, [
                    _createElementVNode("div", _hoisted_138, [
                      _createElementVNode("div", {
                        class: "task-filename",
                        title: task.filename
                      }, _toDisplayString(task.filename), 9, _hoisted_139),
                      _createElementVNode("div", _hoisted_140, [
                        _createElementVNode("span", {
                          class: _normalizeClass(["status-badge", task.status])
                        }, _toDisplayString(task.status === "pending" ? "等待中" : task.status === "uploading" ? "上传中" : task.status === "completed" ? "已完成" : task.status === "cancelled" ? "已取消" : task.status === "duplicate" ? "已存在" : "上传失败"), 3)
                      ])
                    ]),
                    _createElementVNode("div", _hoisted_141, [
                      _createElementVNode("div", _hoisted_142, [
                        _createElementVNode("div", {
                          class: _normalizeClass(["task-progress-fill", task.status]),
                          style: _normalizeStyle({ width: task.progress + "%" })
                        }, null, 6)
                      ]),
                      _createElementVNode("span", _hoisted_143, _toDisplayString(task.progress) + "%", 1)
                    ]),
                    _createElementVNode("div", _hoisted_144, [
                      task.status === "uploading" ? (_openBlock(), _createElementBlock("button", {
                        key: 0,
                        onClick: ($event) => cancelUpload(task.id),
                        class: "task-cancel-btn",
                        title: "取消上传"
                      }, [..._cache[104] || (_cache[104] = [
                        _createElementVNode("svg", {
                          viewBox: "0 0 24 24",
                          width: "16",
                          height: "16"
                        }, [
                          _createElementVNode("path", {
                            fill: "currentColor",
                            d: "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"
                          })
                        ], -1)
                      ])], 8, _hoisted_145)) : _createCommentVNode("", true),
                      task.error ? (_openBlock(), _createElementBlock("span", {
                        key: 1,
                        class: "error-message",
                        title: task.error
                      }, _toDisplayString(task.error), 9, _hoisted_146)) : _createCommentVNode("", true)
                    ])
                  ], 2);
                }), 128))
              ]))
            ])
          ])
        ], 2)) : _createCommentVNode("", true),
        _createElementVNode("div", {
          class: _normalizeClass(["notification", { "show": showNotification.value, "success": notificationType.value === "success", "error": notificationType.value === "error" }])
        }, [
          notificationType.value === "success" ? (_openBlock(), _createElementBlock("svg", _hoisted_147, [..._cache[105] || (_cache[105] = [
            _createElementVNode("path", {
              fill: "currentColor",
              d: "M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"
            }, null, -1)
          ])])) : _createCommentVNode("", true),
          notificationType.value === "error" ? (_openBlock(), _createElementBlock("svg", _hoisted_148, [..._cache[106] || (_cache[106] = [
            _createElementVNode("path", {
              fill: "currentColor",
              d: "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"
            }, null, -1)
          ])])) : _createCommentVNode("", true),
          _createElementVNode("span", null, _toDisplayString(notificationMessage.value), 1)
        ], 2)
      ]);
    };
  }
});

const Page = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-ba490599"]]);

export { Page as default };
