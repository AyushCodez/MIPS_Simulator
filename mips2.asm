addi $t1, $0, 5
addi $t2,$gp,0
addi $t3, $gp, 0
addi $t3, $t3, 20
addi $t4, $0, 0 # initialize i = 0
addi $t5, $t2, 0 # address to read
addi $t6, $t3, 0 # address to write
j copy_sorted

begin_sort:
	addi $t4, $0, 0 # initialize i = 0

outer_loop:
	addi $t9, $t3, 0 # read address
	beq $t4, $t1, end_outer_loop # ending loop at i == n
	addi $t5, $0, 0 # j = 0
	addi $s0, $0, 0 # swapped = 0
	sub $t6, $t1, $t4 # n - i
	sub $t6, $t6, 1 # n - i - 1
	j inner_loop # goes inside inner loop

inner_loop:
	beq $t5, $t6, end_inner_loop # ending inner loop at j = n - i - 1
	lw $s1, 0($t9) # loads a[j]
	lw $s2, 4($t9) # loads a[j+1]
	sub $s3, $s2, $s1
	slt $s4, $s3, $0
	addi $s5, $0, 1
	beq $s4, $s5, swap
#	bgtz $s3, swap # swaps a[j] and a[j+1] if a[j] > a[j+1]
	
back_from_swap:
	addi $t9, $t9, 4 # increments memory read location (basically incrementing j for memory)
	addi $t5, $t5, 1 # increments j
	j inner_loop
	
end_inner_loop:
	beq $s0, $0, end_outer_loop # if no swap was done, ends outer loop
	addi $t4, $t4, 1 # increment i
	j check_swapped # checks if swap was done or not

swap: # $t9 =  a[j], $t8 = a[j+1], $t7 = temp
    lw $t7, 0($t9)    # load a[j] into $t7
    lw $t8, 4($t9)    # load a[j+1] into $t8
    sw $t8, 0($t9)    # store a[j+1] to a[j]
    sw $t7, 4($t9)    # store temp (a[j]) to a[j+1]
    addi $s0, $0, 1         # set swapped to 1
    j back_from_swap

check_swapped:
	beq $s0, $0, end_outer_loop # ends outerloop if swapped
	j outer_loop

copy_sorted:
	beq $t4, $t1, begin_sort
	lw $t7, 0($t5) # read from sorted array
	sw $t7, 0($t6) # store in given location
	# increment counters
	addi $t4, $t4, 1
	addi $t5, $t5, 4
	addi $t6, $t6, 4
	j copy_sorted
	
end_outer_loop: addi $a0,$0,0