$(".nav-item a").on("click", function(){
    $(".nav").find(".active").removeClass("active");
    $(this).parent().addClass("active");
 });

function copy(that){
var inp =document.createElement('input');
document.body.appendChild(inp)
inp.value =that.textContent
inp.select();
document.execCommand('copy',false);
inp.remove();
}

document.body.style.zoom="90%"

function copynew(that) {
    var text = that;
    console.log(text)
    navigator.clipboard.writeText(text);
}