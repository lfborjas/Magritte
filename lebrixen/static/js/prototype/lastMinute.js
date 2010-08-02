var esText = "No obstante, no parece que se pueda transmitir información clásica a velocidad superior a la de la luz mediante el entrelazamiento porque no se puede transmitir ninguna información útil a más velocidad que la de la luz. Sólo es posible transmitir de información usando un conjunto de estados entrelazados en conjugación con un canal de información clásico, también llamado teleportación cuántica.";
var enText = "Very often, such as with climate change, this leaves the public with the impression that disagreement within the scientific community is much greater than it actually is ";

$(function(){
		function toggleDialog(key){
			if($('#caption').dialog('isOpen')){
				$('#caption').dialog('close');
			}else{
				$('#caption').dialog('open');
			}
			$('#cue').text(key-48)
		}
		
				
		$('#caption').dialog({			
			modal: true,
			autoOpen : false,
			width: 500,
		});
		
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
				else if(key === 49){ //1
					$('#caption').html("<p>When you write, you must be context aware. But <em>time can be your enemy</em></p>");
					toggleDialog(key);
				}
				else if(key === 50){ // 2 ...
					$('#caption').html("<p>Serendipitron can help: it reads what you write <em>in real time</em></p>");
					toggleDialog(key);
				}
				else if(key === 51){
					$('#caption').html("<p>And recommends useful, and related, stuff from the internet: so you know <em>what's been said</em> about the subjects of your work</p>");
					toggleDialog(key);
				}
				else if(key === 52){
					$('#caption').html("<p>Not only in english...</p>");
					toggleDialog(key);
				}
				else if(key === 53){
					$('#caption').html("<p>It'll learn about <em>your</em> favorite topics, so the recommendations are personalized and <em>not generic</em></p>");
					toggleDialog(key);
				}
				else if(key === 54){
					$('#caption').html("<p>You don't have to come to serendipitron for help: it'll <em>come to you</em> in your favorite blog engine, word processor or whatever, <em>just ask for it!</em>...</p>");
					toggleDialog(key);
				}
				else if(key === 55){
					$('#caption').html("<p>... Or do it yourself, with the <em>API for developers</em></p>");
					toggleDialog(key);
				}
				//LEFT = english text
				if(key=== 37){
					$('#id_content').val(enText);
					$('#id_content').trigger('paste');
				}
				
				
				
			}//if not a text or a select
		}); // end of keybindings
});