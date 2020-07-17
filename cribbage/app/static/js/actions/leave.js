export function announcePlayerLeave(msg) {
  $("#" + msg.nickname).remove();
  $('.game-log').append('<br>' + $('<div/>').text(msg.nickname + ' left.').html());
}

export function clearSessionData() {
   sessionStorage.removeItem('nickname');
   sessionStorage.removeItem('gameName');
   sessionStorage.removeItem('ws');
   window.location.href = "/";
}