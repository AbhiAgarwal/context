/**
 * Compress and package CSS and JS with Grunt.
 */
module.exports = function(grunt) {
  config = grunt.file.readJSON('package.json');
  grunt.initConfig({
    pkg: config,

    // Minify css.
    cssmin: {
      css:{
        src: 'galleria.showroom.css',
        dest: 'galleria.showroom.min.css'
      }
    },

    // Minify js.
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
        '<%= grunt.template.today("yyyy-mm-dd") %> - MIT License */' + "\n"
      },
      js: {
        files: {
          'galleria.showroom.min.js' : [ 'galleria.showroom.js' ]
        }
      }
    },

    // Reference minified css from within js.
    'string-replace': {
      'js': {
        files: {
          'galleria.showroom.min.js' : [ 'galleria.showroom.min.js' ]
        },
        options: {
          replacements: [{
            pattern: /galleria\.showroom\.css/ig,
            replacement: 'galleria.showroom.min.css?v' + config.version
          }]
        }
      }
    },

    // Watch for changes.
    watch: {
      files: ['galleria.showroom.css', 'galleria.showroom.js'],
      tasks: ['cssmin', 'uglify']
    }
  });
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-string-replace');
  grunt.registerTask('default', [ 'cssmin:css', 'uglify:js', 'string-replace:js']);
};
