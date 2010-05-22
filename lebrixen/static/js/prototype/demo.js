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
	});
});
