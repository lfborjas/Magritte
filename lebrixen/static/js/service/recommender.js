/*Namespace for handling recommendations
 * @author: lfborjas
 * 
 * Notes: the token for the default app is 0a0c8647baf451dc081429aa9815d476
 */
if(!window.RECOMMENDER){
	RECOMMENDER = {
			/*The urls to diverse service calls*/
			_service_root: "http://lebrixen.com",
			//initial call url:
			_init_call: "api/startSession",
			
			/*Internal data*/
			_lastContext: "",
			_lastLength: 0,
			_triggerWords: 2,
			_wordsDiff: 0,
			_diff: 0,
			
			/*Interface data*/
			
			/*Web service call functions*/
			extractTerms: function(){
				if($('#id_content').val()){
					$.get('/getTerms/',
							{context: $('#id_content').val(),lang: $('#id_lang').val(), service:$('#id_service').val()},
							function(data){
								if(data){					
									$('#terms-title').show();						
									$('#terms').val(data.terms);					
									$('#terms').effect('highlight');
									//$('#terms').trigger('change');
									RECOMMENDER.doQuery();
								}
							},
							'json'
					);
				}
			}, //end of extractTerms definition
			
			detectContextChange: function(e){
				   if(e.which == 32){ RECOMMENDER._diff ++;}
					
				   //primitive context change sensibility: lexical comparison...
				   //start detecting the context after the initial words treshold
				   wordcount = $('#id_content').val().split(' ').length;
				   if(wordcount >= RECOMMENDER._triggerWords && RECOMMENDER._diff >= RECOMMENDER._wordsDiff){
					   if(wordcount != RECOMMENDER._lastLength && $('#id_content').val() != RECOMMENDER._lastContext){			   
						   RECOMMENDER._lastContext = $('#id_content').val();
						   RECOMMENDER._lastLength = wordcount;
						   RECOMMENDER._diff = 0;
						   //call the extraction method:
						   RECOMMENDER.extractTerms();
					   }
				   }					
			},//end of detectContextChange definition
			
			doQuery: function(){
				$.get('/search/',
						{q: $('#terms').val(), hl: $('#id_lang').val()},
						function(data){
							$('#docs-container').html("");
							if(!data){
								$('#docs-title').hide();
							}else{
								$('#docs-title').show().text("Documentos Recomendados ("+data.length+")");
							}
							$.each(data, function(index, hit){					
								$('#docs-container').append('<div class="result" id="doc_'+hit.id+'">'+
												   '<a target="_blank" href="'+hit.url+'"><strong>'+hit.title+'</strong></a>'+									    
												   '<p>'+hit.summary+'</p>'+									   
												 '</li>');
								
							});
							$('#docs').effect('highlight');
							if(!$('.trigger').hasClass('active'))
								$('.trigger').addClass("active");
							$('.trigger').effect("pulsate", {times:5}, 2000);
						},
						'json');
			},//end of doQuery definition
			
	}//end of namespace RECOMMENDER
}

$(document).ready(function() {
	/*When the words in the content area reach a treshold, call the extract terms event*/
   $('#id_content').keyup(RECOMMENDER.detectContextChange);
   //$('#terms').change(doQuery);
   $('#id_service').change(RECOMMENDER.extractTerms);
   
   //to toggle the bar
   $(".trigger").click(function(){
		$(".panel").toggle("fast");
		//$(this).toggleClass("active");
		return false;
	});
   return false;
});