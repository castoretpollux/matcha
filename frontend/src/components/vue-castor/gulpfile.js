// Import gulp and plugins
const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const concat = require('gulp-concat');
const sourcemaps = require('gulp-sourcemaps');

// Define a task to compile SCSS to CSS
function compileSass() {
    return gulp.src('./src/*.scss')  // Source folder for SCSS files
        .pipe(sourcemaps.init())             // Initialize sourcemaps
        .pipe(sass().on('error', sass.logError)) // Compile SCSS and log errors
        .pipe(concat('castor.renderers.css'))
        .pipe(sourcemaps.write('./maps'))    // Write sourcemaps
        .pipe(gulp.dest('./'));      // Destination folder for CSS files
}


// Export tasks
exports.build = compileSass;