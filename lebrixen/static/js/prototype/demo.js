$(function(){
	//bind some keys to the document ready:
	//based on http://seriouscoding.com/keyboard-navigation-with-javascript-and-jquer
	$(document).keydown(function(event){
		var key = event.keyCode || event.which;
		var element="";		
		if(event.target.type !== 'text' && event.target.type !== 'select'){
			//LEFT = graph
			if(key=== 37){
				element = '#user-profile img';
			}
			//UP=tools
			else if(key===38){
				element = '#tools';
			}
			//RIGHT=simulation unranked
			else if(key===39){
				element = "#simulation-unranked";
			}
			//DOWN = simulation ranked
			else if(key===40){
				element = "#simulation-ranked";
			}
			$(element).effect('highlight', {color: '#f6f6f6'}, 1000);
			
		}//if not a text or a select
	}); // end of keybindings
	
	//get users of an app:
	$('#id_appId').change(function(e){
		if($(this).val()){
			$.get('/prototype/getUsers/',
					{appId: $(this).val()},
					function(data){
						$.each(data, function(index, user){
							$('#id_appUser').append('<option value="'+user.k+'">'+user.val+'</option>');
						});
						$('#tools-submit').removeAttr('disabled');
					},
					'json'
			);
		}else{
			$('#tools-submit').attr('disabled','disabled');
			$('#id_appUser').empty();
		}
	});
	
	//set the appropiate profile
	$('#tools-form').submit(function(e){
		e.preventDefault();
		$.getJSON('/api/demo/setProfile/',
				$('#tools-form').serialize(),
				function(data){
					//alert(data.graph_request);
					$('.user-info').text("Perfil actual: "+ $('#id_appUser :selected').text().replace( /^\s+|\s+$/g, '')
										 +", usuario de "+$('#id_appId :selected').text().replace( /^\s+|\s+$/g, ''))
					//given the request, ask for it async
				});
	});
});
