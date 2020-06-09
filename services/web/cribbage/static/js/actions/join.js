export function announcePlayerJoin(msg) {
  if ($("#" + msg.nickname).length === 0) {
    let playerName = $('<span/>', {
      class: 'player-name',
      html: msg.nickname
    });

    let playerPoints = $('<span/>', {
      class: 'player-points',
      html: msg.points
    });

    let panelHeading = $('<div/>', {
      class: 'panel-heading',
    });

    let panelBody = $('<div/>', {
      id: msg.nickname + '-cards',
      class: 'panel-body d-flex justify-content-center',
    });

    panelHeading.append(playerName);
    panelHeading.append(playerPoints);

    let opponentPanel = $('<div/>', {
      id: msg.nickname,
      class: 'opponent rounded panel panel-default',
    });

    opponentPanel.append(panelHeading);
    opponentPanel.append(panelBody);
    $('.opponents').append(opponentPanel);

    $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
  }
}