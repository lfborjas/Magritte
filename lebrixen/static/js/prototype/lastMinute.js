var esText = "La referencia freudiana en la investigación del inconsciente lleva la marca de cierto sello psíquico; los procesos psíquicos inconscientes que Freud circunscribió se encuentran en el principio del propio descubrimiento que el mismo hizo"
var enText = "the conventional view of the research process is that we first derive a set of hypotheses from a theory, design and conduct a study to test these hypotheses, analyze the data to see if they were confirmed or disconfirmed, and then chronicle this sequence of events in the journal article"
$(function(){
		$(document).keydown(function(event){
			var key = event.keyCode || event.which;
			var element="";		
			if(event.target.type !== 'text' && event.target.type !== 'select'){
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
					window.location.replace($('#demo-link').attr('href'));
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