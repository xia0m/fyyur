const delete_venue_button = document.querySelector('.delete-venue')
if(delete_venue_button){
delete_venue_button.onclick = function(e){
  const venueId = e.target.dataset['id'];
  const host_address = window.location.origin
  fetch('/venues/' + venueId, {
      method:'DELETE'
  })
  .then(function(){
      window.location.replace(host_address);
  })
  .catch(function(error){
      console.log('Error delete venue ', error)
  })
}}