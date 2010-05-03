var lastContext = "";
var lastLength = 0;
var triggerWords = 10;
var spaceBarCode = 32;
var wordsDiff = 5; //the word count interval in which to trigger the event
var diff = 0;
//var words = 0;

function extractTerms(){
	$.get('/getTerms/',
			{context: $('#id_content').val(),lang: $('#id_lang').val(), service:$('#id_service').val()},
			function(data){
				if(data){
					$('#terms').val(data.terms);
					$('#terms').effect('highlight');
				}
			},
			'json'
			);
}

/*Be as lazy as possible in context detection, but determine it efectively*/
function detectContextChange(e){
	   if(e.which == spaceBarCode){ diff ++;}
	
	   //primitive context change sensibility: lexical comparison...
	   //start detecting the context after the initial words treshold
	   wordcount = $('#id_content').val().split(' ').length;
	   if(wordcount >= triggerWords && diff >= wordsDiff){
		   if(wordcount != lastLength && $('#id_content').val() != lastContext){			   
			   lastContext = $('#id_content').val();
			   lastLength = wordcount;
			   diff = 0;
			   //call the extraction method:
			   extractTerms();
		   }
	   }
}

$(document).ready(function() {
	/*When the words in the content area reach a treshold, call the extract terms event*/
   $('#id_content').keyup(detectContextChange);
});