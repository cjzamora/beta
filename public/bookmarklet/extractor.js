;(function() {
    // compiled training data
    var training = [];
    // possible labels
    var LABELS   = ['title', 'srp', 'discounted', 'description'];

    // add trim functionality
    // String.prototype.trim = function(string) {
    //     return (string !== undefined || string !== null) ? string.replace(/^\s+|\s+$/g, '') : '';
    // };

    // well nodelist doesn't have it's own iterator
    NodeList.prototype.forEach = Array.prototype.forEach;

    // this thing has also no iterator
    CSSStyleDeclaration.prototype.forEach = Array.prototype.forEach;

    // this thing has also no iterator
    DOMTokenList.prototype.forEach = Array.prototype.forEach;

    // global utility functions
    window._utils = {
        // trim string
        trim    : function(string) {
            return (string) ? string.replace(/^\s+|\s+$/g, '') : '';
        },

        // clean string
        clean : function(string) {
            return (string) ? string.replace(/\r?\n|\r/g, '') : '';
        },

        // check if valid
        isValid : function(value) {
            var re = /^[a-zA-Z][a-zA-Z0-9\-_]+$/;

            return value && re.test(value);
        },

        // get element bound
        bound   : function(element) {
            // get scroll top
            var scrollTop  = document.documentElement.scrollTop  || document.body.scrollTop;
            // get scroll left
            var scrollLeft = document.documentElement.scrollLeft || document.body.scrollLeft;

            // get bounding client rectangle
            var rect = element.getBoundingClientRect();

            return {
                width   : rect.width,
                height  : rect.height,
                left    : rect.left + scrollLeft,
                top     : rect.top + scrollTop
            };
        },

        // get element description
        element : function(element, nameOnly) {
            var name = element.tagName.toLowerCase();
            var self = this;

            if(nameOnly) {
                return name;
            }

            var classes = [];

            element.classList.forEach(function(key) {
                if(self.isValid(key)) {
                    classes.push(key);
                }
            });

            return {
                name    : name,
                id      : this.isValid(element.id) ? element.id : '',
                classes : classes.sort()
            };
        },

        // generate tag path
        path : function(element, nameOnly) {
            var path = [];

            while(element) {
                if(element === document.body) {
                    break;
                }

                path.splice(0, 0, this.element(element, nameOnly))

                element = element.parentElement;
            }

            path.sort()

            return path;
        },

        // calculate computed css
        computed : function(element) {
            // get default computed style
            var defaults = document.defaultView.getComputedStyle(document.body);
            // get the computed style for target element
            // var computed = document.defaultView.getComputedStyle(element);
            var computed = window.getComputedStyle(element);

            var data = {};

            computed.forEach(function(key) {
                // don't care about dimension, let bound track that
                if(['width', 'height', 'top', 'left', 'right', 'bottom'].indexOf(key) !== -1) {
                    return;
                }

                // don't care about webkit specific
                if(key.charAt(0) === '-') {
                    return;
                }

                // don't care about default value
                if(computed[key] === defaults[key]
                && ['font-weight'].indexOf(key) === -1) {
                    return;
                }

                data[key] = computed[key];
            });

            return data;
        }
    };

    // extract meta data
    data = function() {
        var titles          = [];
        var descriptions    = [];
        var gold_text       = [];

        // iterate on each titles
        document
        .querySelectorAll('title')
        .forEach(function(el) {
            titles.push(_utils.trim(el.innerText));
            gold_text.push(_utils.trim(el.innerText))
        });

        // iterate on each meta descriptions
        document
        .querySelectorAll('meta[name="description"]')
        .forEach(function(el) {
            descriptions.push(el.content);
            gold_text.push(el.content);
        });

        // open graph title
        document
        .querySelectorAll('meta[name="og:title"], meta[property="og:title"]')
        .forEach(function(el) {
            titles.push(_utils.trim(el.content));
            gold_text.push(_utils.trim(el.content));
        });

        // open graph description
        document
        .querySelectorAll('meta[name="og:description"], meta[property="og:description"]')
        .forEach(function(el) {
            descriptions.push(el.content);
            gold_text.push(el.content);
        });

        // twitter title
        document
        .querySelectorAll('meta[name="twitter:title"], meta[property="twitter:title"]')
        .forEach(function(el) {
            titles.push(_utils.trim(el.content));
            gold_text.push(_utils.trim(el.content));
        });

        // twitter description
        document
        .querySelectorAll('meta[name="twitter:description"], meta[property="twitter:description"]')
        .forEach(function(el) {
            descriptions.push(el.content);
            gold_text.push(_utils.trim(el.content));
        });

        return {
            url             : window.location.href,
            hostname        : window.location.hostname,
            titles          : titles,
            descriptions    : descriptions,
            gold_text       : gold_text
        }
    }();

    // extract body
    data.body = function() {
        // computed style for body
        var computed = {};

        // iterate on each computed styles
        document
        .defaultView
        .getComputedStyle(document.body)
        .forEach(function(key) {
            // don't care about webkit specific
            if(key.charAt(0) === '-') {
                return;
            }

            // don't care about default value
            computed[key] = document.defaultView.getComputedStyle(document.body)[key];
        });

        return {
            scroll : {
                top  : document.documentElement.scrollTop  || document.body.scrollTop,
                left : document.documentElement.scrollLeft || document.body.scrollLeft
            },
            bound       : _utils.bound(document.body),
            computed    : computed
        }
    }();

    // extract texts
    data.texts = function() {
        var texts = [];
        var ext   = [];

        // walk over all text in the page
        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);

        // iterate on each node
        while(text = walker.nextNode()) {
            // no text?
            if(_utils.trim(text.nodeValue).length === 0) {
                continue;
            }

            // container node
            var node  = text.parentElement
            // get element bound
            var bound = _utils.bound(node);
            // get element name
            var name  = _utils.element(node, true);

            // skip styles and scripts
            if(['style', 'script', 'noscript'].indexOf(name) !== -1) {
                continue;
            }

            // no bound? skip it ..
            if((bound.width * bound.height) < 0) {
                continue;
            }

            // has inner text?
            if(node.innerText.length > 0) {
                // have we seen this node?
                if(node.__features) {
                    // just push the text
                    node.__features.text.push(_utils.clean(_utils.trim(text.nodeValue)));
                    continue;
                }

                setNodeFeatures(node);
            }

            // find the parent node that is a block
            while(node) {
                // get computed styles
                // var computed = document.defaultView.getComputedStyle(node);
                var computed = window.getComputedStyle(node);

                // do we find the block parent?
                if((parseInt(computed.width) * parseInt(computed.height)) > 0) {
                    break;
                }

                // get parent element
                node = node.parentElement;

                // still a valid node?
                if(!node) {
                    break;
                }
            }

            // parent element is ul?
            if(node.parentElement.tagName == 'UL') {
                // have we seen this node?
                if(node.parentElement.__features) {
                    // just push the text
                    node.parentElement.__features.text.push(_utils.clean(_utils.trim(text.nodeValue)));
                } else {
                    setNodeFeatures(node.parentElement);
                }
            }

            // have we seen this node?
            if(node.__features) {
                // just push the text
                node.__features.text.push(_utils.clean(_utils.trim(text.nodeValue)));
                continue;
            }

            setNodeFeatures(node);
        }

        // iterate on each node
        for(var i in ext) {
            // create element
            var d = document.createElement('div');
            // get node text
            var t = ext[i].__features.text.join(' ').substring(0, 60);

            // is this our annotator?
            if(ext[i].getAttribute('data-annotate-id') !== null) {
                continue;
            }

            ext[i].style.position = 'relative';

            d.innerText             = '+';
            d.style.boxSizing       = 'border-box';
            d.style.backgroundColor = 'rgba(255, 0, 0, 0.8)';
            d.style.bottom          = '0px';
            d.style.color           = '#FFFFFF';
            d.style.cursor          = 'pointer';
            d.style.fontFamily      = 'Arial, sans-seif';
            d.style.fontSize        = '8px';
            d.style.height          = '8px';
            d.style.lineHeight      = '9px';
            d.style.padding         = '0px 2px';
            d.style.position        = 'absolute';
            d.style.minWidth        = '9px';

            if(!ext[i].__features.parent) {
                d.style.right = '0px';
            }

            // set annotation index
            d.setAttribute('data-annotate-id', i);

            // set annotator
            d.onclick = annotateElement;

            ext[i].appendChild(d);
        }       

        // annotate element
        function annotateElement(e) {
            // get annotation label
            var label   = prompt('Enter element label: ');
            // get node index
            var id      = e.target.getAttribute('data-annotate-id');

            // if label is valid
            if(LABELS.indexOf(label) === -1) {
                return;
            }

            // set annotation label
            data.texts[id].label = label;
            // set text
            e.target.innerText = e.target.innerText + ' (' + label.toUpperCase() + ') ';
        };

        // set node data helper
        function setNodeFeatures(node) {
            // collect features
            node.__features = {
                label    : 'unknown',
                element  : _utils.element(node),
                path     : _utils.path(node, true),
                selector : _utils.path(node),
                text     : [_utils.clean(_utils.trim(text.nodeValue))],
                html     : node.innerHTML,
                bound    : _utils.bound(node),
                computed : _utils.computed(node),
                parent   : true
            }

            // push text features
            texts.push(node.__features);

            // push extracted
            ext.push(node);

            // debug
            node.style.border = '1px solid red';
        };

        return texts;
    }();

    // extract images
    data.images = function() {
        var images = [];

        // iterate on all images
        document
        .querySelectorAll('img[src]')
        .forEach(function(el) {
            var bound = _utils.bound(el);

            // has a valid bound?
            if((bound.width * bound.height) === 0) {
                return;
            }

            // push images
            images.push({
                src      : el.src,
                element  : _utils.element(el),
                path     : _utils.path(el, true),
                selector : _utils.path(el),
                bound    : bound,
                computed : _utils.computed(el)
            });

            // debug
            el.style.border = '1px solid red';
        })

        return images;
    }();

    // extract links (not execute this for the meantime)
    data.links = function() {
        var links = [];

        document
        .querySelectorAll('a[href]')
        .forEach(function(el) {
            links.push(el.href);
        });

        return links;
    };

    // generate training data button
    var button = document.createElement('button');

    button.id               = 'annotateGenerate';
    button.innerText        = 'Generate Training Data';
    button.style.padding    = '10px 50px';
    button.style.position   = 'fixed';
    button.style.bottom     = '10px';
    button.style.right      = '10px';

    // on button click
    button.onclick = function(e) {
        // iterate on each extracted node
        for(var i in data.texts) {
            // feature set
            var set = {
                href        : encodeURIComponent(window.location.href),
                bound       : data.texts[i].bound,
                computed    : data.texts[i].computed,
                element     : data.texts[i].element,
                label       : data.texts[i].label,
                path        : data.texts[i].path
            };

            // unknown label?
            if(set.label !== 'unknown') {
                // push it on top
                training.unshift(set);

                continue;
            }

            // push on bottom
            training.push(set);
        }

        var request = new XMLHttpRequest();

        request.open('POST', window.__SERVER_URL + 'index.php', true);
        request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

        request.onreadystatechange = function(){
            if (request.readyState != 4) {
                return;
            }

            if (request.status != 200 && request.status != 304) {
                alert('HTTP error ' + req.status);
                return;
            }

            var response = request.responseText;

            alert(response);
        }

        request.send('training=' + JSON.stringify({ 'training' : training, 'href' : encodeURIComponent(window.location.href) }));
    };

    document.body.appendChild(button);
})();