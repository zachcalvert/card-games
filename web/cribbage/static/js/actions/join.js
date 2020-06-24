export function announcePlayerJoin(msg) {
  if ($("#" + msg.nickname).length === 0) {
    let playerName = $('<span/>', {
      class: 'player-nickname opponent-nickname',
      html: msg.nickname
    });

    let playerPoints = $('<span/>', {
      class: 'player-points opponent-points',
      html: msg.points
    });

    let panelHeading = $('<div/>', {
      class: 'panel-heading',
    });
    panelHeading.append(playerName);
    panelHeading.append(playerPoints);

    let panelBody = $('<div/>', {
      id: msg.nickname + '-cards',
      class: 'panel-body d-flex justify-content-center',
    });
    let playPile = $('<div/>', {
      class: 'play-pile',
    });


    let opponentPanel = $('<div/>', {
      id: msg.nickname,
      class: 'opponent rounded panel panel-default',
    });

    opponentPanel.append(panelHeading);
    opponentPanel.append(panelBody);
    opponentPanel.append(playPile);
    $('.opponents').append(opponentPanel);

    $('.game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
  }
}