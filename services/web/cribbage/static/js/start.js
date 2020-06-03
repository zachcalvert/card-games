export function start(msg) {
  console.log('started with players: ' + msg.players);
  $('#action-button').html('Deal');
}