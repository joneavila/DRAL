function plotFeatures(signal, sampleRate, featureSet, monster, ...
    frameOfFocus, figureTitle)
% PLOTFEATURES Plot the features computed with MAKETRACKMONSTER, for a
% specified frame of focus. The figure has a "Play audio" button to play
% the portion of the signal for the relevant features.
%
% [!] The features' Y-axis minimum and maximum are relative to the values
%     being displayed, not relative to the entire `monster` (return value
%     of MAKETRACKMONSTER).

    [featuresTimeTables, fragSignal] = featuresToTimeTables(featureSet, ...
        monster, signal, sampleRate, frameOfFocus);

    fig = figure('Position', [680 557 1000 800]);

    set(fig, 'name', figureTitle);

    %% Plot the features.
    % As of MATLAB R2022b, stackedplot can plot variables from multiple
    % tables and timetables in a stacked plot.
    s = stackedplot(featuresTimeTables, 'Color', 'blue', ...
        'LegendVisible', 'off');
    
    %% Wait for the stacked plot to load (polling).
    delay = 0.01;
    while isempty(s.NodeChildren)
        pause(delay);
    end

    %% Create the audio player.
    % Set the audio to play.
    audioPlayer = audioplayer(fragSignal, sampleRate);
    
    % Set the function to execture at start of playback.
    audioPlayer.set('StartFcn', @audioPlayerStartFn);

    % Set the function to execute repeatedly during playback.
    audioPlayer.set('TimerFcn', @audioPlayerCallback);
    
    % Set the seconds between audio player's callback function.
    frameRate = 90;
    timerPeriod = 1/frameRate;
    audioPlayer.set('TimerPeriod', timerPeriod);
    
    %% Add a play button to the figure.
    uicontrol(fig, 'style','push',...
        'units','pix',...
        'position',[10 10 180 40],...
        'fontsize',12,...
        'string','Play audio',...
        'callback', {@playButtonCallback, audioPlayer} ...
    );
    
    function audioPlayerStartFn(~, ~)
        % To each set of axes in the stack plot, add a line plot with the
        % tag 'player'. These line plots will be updated during playback.
        axes = findobj(s.NodeChildren, 'Type','Axes');
        for axNum = 1:length(axes)
            ax = axes(axNum);
            hold(ax, 'on')
            plot(ax, [0 0], ax.YLim, 'Color', '#E85F5C', ...
                'LineWidth', 1, 'Tag', 'player');
        end
    end

    function audioPlayerCallback(audioPlayer, ~)
        % For each set of axes in the stack plot, update the line with the
        % tag 'player' to indicate the current second being played.
        currentlyPlayingSeconds = get(audioPlayer, 'CurrentSample') / ...
            get(audioPlayer, 'SampleRate');
        axes = findobj(s.NodeChildren, 'Type','Axes');
        for axNum = 1:length(axes)
            ax = axes(axNum);
            hold(ax, 'on')
            playerLine = findobj(ax.Children, 'Tag', 'player');
            set(playerLine, 'XData', ...
                [currentlyPlayingSeconds currentlyPlayingSeconds])
        end
    end

    function playButtonCallback(~, ~, audioPlayer)
        % Wait for the playback to complete.
        playblocking(audioPlayer);
    end

end