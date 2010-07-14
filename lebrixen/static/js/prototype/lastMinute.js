var esText = "No obstante, no parece que se pueda transmitir información clásica a velocidad superior a la de la luz mediante el entrelazamiento porque no se puede transmitir ninguna información útil a más velocidad que la de la luz. Sólo es posible la transmisión de información usando un conjunto de estados entrelazados en conjugación con un canal de información clásico, también llamado teleportación cuántica. Mas, por necesitar de ese canal clásico, la información útil no podrá superarla.";
//var enText = "Yet another interpretation of this phenomenon is that quantum entanglement does not necessarily enable the transmission of classical information faster than the speed of light because a classical information channel is required to complete the process";
var enText = esText;
$(function(){
		$(document).keydown(function(event){
			var key = event.keyCode || event.which;
			var element="";		
			if(event.target.type !== 'textarea' && event.target.type !== 'select'){
				//UP=settings
				if(key===38){
					if($('#settings').is(':hidden')){
						$('#settings').show();
					}else{
						$('#settings').hide();
					}
				}				
				//DOWN = simulation
				else if(key===40){
					//$('#demo-link').click();
					//window.location.replace($('#demo-link').attr('href'));
					window.open($('#demo-link').attr('href'), "_blank")
				}
				//RIGHT: spanish text:
				else if(key===39){
					$('#id_content').val(esText);
					$('#id_content').trigger('paste');
				}
				//LEFT = english text
				if(key=== 37){
					$('#id_content').val(enText);
					$('#id_content').trigger('paste');
				}
				
				
				
			}//if not a text or a select
		}); // end of keybindings
});