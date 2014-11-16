Showroom Galleria Theme
========

A responsive widescreen slideshow theme for [Galleria.io](http://Galleria.io).

This Galleria Theme was designed to display rooms and rental properties for [Roomify](http://Roomify.us), a Drupal-based booking engine for Hotels, BnBs, and Vacation Rentals.

### Demo

[View the responsive demo](http://bluesparklabs.github.io/showroom/).

### Requirements

The showroom theme has been tested with [Galleria 1.3.3](http://galleria.io/static/galleria-1.3.3.zip) and is expected to work with the latest version as well.


### Installation

* [Download the latest version of Galleria](http://galleria.io/download/) and unzip somewhere in your website project. For Drupal projects, the extracted folder is usually placed at `sites/all/libraries/galleria`.
* Download the Showroom Theme and expand it in the `themes` folder inside Galleria.
* Read Galleria's documentation about [using themes](http://galleria.io/docs/themes/using_themes/) for further information.

### Usage

The Galleria Showroom Theme is responsive out-of-the-box:

<pre>

    &lt;div id="galleria"&gt;
        &lt;a&gt;&lt;img ...&gt;&lt;/a&gt;
        &lt;a&gt;&lt;img ...&gt;&lt;/a&gt;
        &lt;a&gt;&lt;img ...&gt;&lt;/a&gt;
    &lt;/div&gt;

    &lt;script&gt;
    // Load the showroom theme
    Galleria.loadTheme('galleria.showroom.min.js');

    // Initialize Galleria
    Galleria.run('#galleria');
    &lt;/script&gt;
</pre>

The responsive resizing is controled by specifying an intrinsic aspect ratio in the CSS. The default aspect ratio, seen below, is set to the standard widescreen format of <code>16:9</code>, with the following CSS rule:

    .galleria-container:before {
        padding-bottom: 56.25%;
    }


The aspect ratio may be adjusted to any value in your site's CSS. The formula to calculate the value to use for the `padding-bottom` is:

    height / width * 100%;


### Problems, Support, Feedback

Use the issue queue at Github to report feedback or file bugs.  Pull requests are gladly welcome.


### Credits

The Showroom theme for Galleria is [a Bluespark production](http://bluespark.com), designed by Rick Cecil, Rusty Segars, and James Wilson.
