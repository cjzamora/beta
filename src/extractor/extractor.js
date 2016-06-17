var system = require('system');
var fs     = require('fs');
var page   = require('webpage').create();
var json   = require('./lib/json2');

// set viewport size
page.viewportSize = {
    width   : 1265,
    height  : 2867
};

// debug info
page.onResourceRequested = function(request) {
    system.stderr.write(JSON.stringify(request, undefined, 2));
    system.stderr.write('\n\n');
};

// debug info
page.onResourceReceived = function(request) {
    system.stderr.write(JSON.stringify(request, undefined, 2));
    system.stderr.write('\n\n');
};

// debug info
page.onConsoleMessage = function(message) {
    system.stderr.write(message);
    system.stderr.write('\n\n');
};

// pretty print
var pretty = function(object) {
    console.log(JSON.stringify(object, undefined, 2));
    console.log('\n\n');
};

// handle page load
page.onLoadFinished = function(status) {
    // unable to load page?
    if(status !== 'success') {
        return phantom.exit();
    }

    var data        = {};

    // put up our helpers
    page.evaluate(function() {
        // add trim functionality
        String.prototype.trim = function(string) {
            return string.replace(/^\s+|\s+$/g, '');
        };

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
                // get the area
                var area = rect.width * rect.height;

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

                    // our target properties
                    if([
                        'font-size',
                        'font-style',
                        'font-weight',
                        'text-decoration'
                    ].indexOf(key) === -1) {
                        return;
                    }

                    data[key] = computed[key];
                });

                return data;
            }
        };
    });

    // extract meta data
    data = page.evaluate(function() {
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
    });

    // extract body
    data.body = page.evaluate(function() {
        return null;

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
    });

    // extract links
    data.links = page.evaluate(function() {
        return null;

        var links = [];

        document
        .querySelectorAll('a[href]')
        .forEach(function(el) {
            links.push(el.href);
        });

        return links;
    });

    // extract texts
    data.texts = page.evaluate(function() {
        var texts = [];
        var ext   = [];

        // walk over all text in the page
        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);

        // iterate on each node
        while(text = walker.nextNode()) {
            // container node
            var node  = text.parentElement
            // get element bound
            var bound = _utils.bound(node);
            // get element name
            var name  = _utils.element(node, true);

            // has parent node?
            if(!node) {
                continue;
            }

            // skip styles and scripts
            if(['style', 'script', 'noscript'].indexOf(name) !== -1) {
                continue;
            }

            // no bound? skip it ..
            if((bound.width * bound.height) < 0) {
                continue;
            }

            // has inner text?
            if(node.innerText && node.innerText.length > 0) {
                // have we seen this node?
                if(node.__features) {
                    // just push the text
                    node.__features.text.push(_utils.clean(_utils.trim(text.nodeValue)));
                    continue;
                }

                setNodeFeatures(node, false);
            }

            // // find the parent node that is a block
            // while(node) {
            //     // get computed styles
            //     // var computed = document.defaultView.getComputedStyle(node);
            //     var computed = window.getComputedStyle(node);

            //     // do we find the block parent?
            //     if((parseInt(computed.width) * parseInt(computed.height)) > 0) {
            //         break;
            //     }

            //     // get parent element
            //     node = node.parentElement;

            //     // still a valid node?
            //     if(!node) {
            //         break;
            //     }
            // }

            // parent element is ul?
            if(node.parentElement.tagName == 'UL') {
                // have we seen this node?
                if(node.parentElement.__features) {
                    // just push the text
                    node.parentElement.__features.text.push(_utils.clean(_utils.trim(text.nodeValue)));
                } else {
                    setNodeFeatures(node.parentElement, true);
                }
            }

            // have we seen this node?
            if(node.__features) {
                // just push the text
                node.__features.text.push(_utils.clean(_utils.trim(text.nodeValue)));
                continue;
            }

            setNodeFeatures(node, true);
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
            d.style.lineHeight      = '9px';
            d.style.padding         = '0px 2px';
            d.style.position        = 'absolute';
            d.style.minWidth        = '9px';

            d.setAttribute('data-annotate-parent', ext[i].__features.parent ? 'true' : 'false');

            if(!ext[i].__features.parent) {
                d.style.right = '0px';
                d.style.backgroundColor = 'rgba(0, 203, 0, 0.8)';
            }

            // set annotation index
            d.setAttribute('data-annotate-id', i);

            // set annotator
            d.onclick = annotateElement;

            // set on mouse over
            d.onmouseover = function (e) { e.target.parentElement.style.backgroundColor = 'rgba(0, 203, 0, 0.8)'; };
            // set on mouse out
            d.onmouseout = function(e) { e.target.parentElement.style.backgroundColor = ''; };

            ext[i].appendChild(d);

            ext[i].onclick = function(e) { e.preventDefault(); };
        }       

        // annotate element
        function annotateElement(e) {
            // get annotation label
            var label   = prompt('Enter element label: ');
            // get node index
            var id      = e.target.getAttribute('data-annotate-id');

            // remove element?
            if(label == 'rem') {
                e.target.parentElement.backgroundColor = '';
                e.target.parentElement.removeChild(this);
                return;
            }

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
        function setNodeFeatures(node, parent) {
            parent = parent ? true : false;

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
                parent   : parent
            }

            // push text features
            texts.push(node.__features);

            // push extracted
            ext.push(node);

            // debug
            node.style.border = '1px solid red';
        };

        return texts;
    });

    // extract images
    data.images = page.evaluate(function() {
        return null;

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
    });

    // set the output path
    var output = system.args[2] + '.json';
    // set the render path
    var render = system.args[2] + '.png';
    
    // save output
    fs.write(output, JSON.stringify(data, undefined, 4));
   
    // render page
    if(system.args.length == 4
    && system.args[3] == 'true') {
        page.render(render);
    }

    return phantom.exit();
};

// invalid arguments?
if(system.args.length < 3) {
    console.log('usage: phantomjs ' + system.args[0] + ' <url> <label> [<render>]');
    phantom.exit();
}

// load page
page.open(system.args[1]);