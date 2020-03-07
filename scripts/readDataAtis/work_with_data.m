arr = load_atis_data("log_td.dat")

timeslice = 1000

acc = zeros(1, ceil(arr.ts(end)/timeslice));

count = 0;
oldts = 0;
index = 1;
for v = 1:size(arr.ts)
    %disp(v);
    %disp("asdf");
    if (arr.ts(v) - oldts) > timeslice
        disp("if");
        count = count + 1;
        acc(1, index) = count;
        count = 0;
        index = index +1;
        oldts = arr.ts(v);
    else
        count = count + 1;
    end
end

plot(acc)