/*
  Common utility file for entire uvi project
  Format of writing:
    * Add the name of file or feature (in case of multiple files) the function is being used in
    * Mention the reference (Ref) if the code is being reused for an external source
*/

/**
 * 
 * @param {object} ctx icon element that has been clicked
 * @param {string} className verbnet class whose link need to be stored; can be a sub-class as well
 * 
 * Function to copy path of the verbnet class/sub-class.
 * Extends the redirection ability of "Class Hierarchy" which is limited to class only (and not sub-classes)
 * Usage in: files with name render_verbnet(_*).html
 */
function copyToClipboard(ctx, className) {
    var classPath = new URL(window.location.origin + className);
    // Ref: https://techoverflow.net/2018/03/30/copying-strings-to-the-clipboard-using-pure-javascript/
    var el = document.createElement('textarea');
    // Set value (string to be copied)
    el.value = classPath.href;
    // Set non-editable to avoid focus and move outside of view
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    // Select text inside element
    el.select();
    // Copy text to clipboard
    var successful = document.execCommand('copy');
    var msg = successful ? 'Copied!' : 'Whoops, not copied!';
    $(ctx).find('i').attr('data-original-title', msg).tooltip('show');
    // Reset the tooltip content but no need to show
    $(ctx).find('i').attr('data-original-title', 'Click to copy link');
    // Remove temporary element
    document.body.removeChild(el);
}
