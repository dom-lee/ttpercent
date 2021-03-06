import math

from django.db.models import Sum, Prefetch, Q, F, Sum
from django.views     import View
from django.http      import JsonResponse
from django.utils     import timezone

from users.utils        import public_login
from deals.models       import Deal, Mortgage, MortgageImage
from investments.models import UserDeal,PaybackSchedule 
from users.models       import User

class DealDetailView(View):
    def get(self, request, deal_id):
        try:
            deal = Deal.objects.get(id=deal_id)
            deal_info = {
                "name"            : deal.name,
                "category"        : Deal.Category(deal.category).label,
                "grade"           : Deal.Grade(deal.grade).label,
                "earningRate"     : deal.earning_rate,
                "repaymentPeriod" : deal.repayment_period,
                "repaymentMethod" : Deal.RepaymentMethod(deal.repayment_method).label,
                "netAmount"       : deal.net_amount,
                "repaymentDay"    : deal.repayment_day,
                "reason"          : deal.reason,
                "debtor"          : deal.debtor.name,
                "creditScore"     : [score.score for score in deal.debtor.creditscore_set.all()],
                "amount"          : deal.userdeal_set.aggregate(total_price=Sum('amount'))['total_price'] or 0,
                "amountPercentage": int((deal.userdeal_set.aggregate(total_price=Sum('amount'))['total_price'] or 0)/deal.net_amount)*100,
            }
            
            if deal.category == Deal.Category.MORTGAGE.value: 
                mortgage = Mortgage.objects.get(deal=deal)
                mortgage_info = {
                    "latitude"               : mortgage.latitude,
                    "longitude"              : mortgage.longitude,
                    "estimatedRecovery"      : mortgage.estimated_recovery,
                    "appraisedValue"         : mortgage.appraised_value,
                    "seniorLoanAmount"       : mortgage.senior_loan_amount,
                    "address"                : mortgage.address,
                    "completedDate"          : mortgage.completed_date,
                    "scale"                  : mortgage.scale,
                    "supplyArea"             : mortgage.supply_area,
                    "usingArea"              : mortgage.using_area,
                    "floor"                  : mortgage.floors,
                    "isUsage"                : mortgage.is_usage,
                    "sellingPointTitle"      : mortgage.selling_point_title,
                    "sellingPointDescription": mortgage.selling_point_description,
                    "mortgageImage"          : [image.image_url for image in mortgage.mortgageimage_set.all()],
                    "collateralReserve"      : mortgage.appraised_value - (mortgage.senior_loan_amount+deal.net_amount)
                }
                return JsonResponse({"dealInfo":deal_info,"mortgageInfo":mortgage_info}, status=200)
            return JsonResponse({"dealInfo":deal_info}, status=200)
            
        except Deal.DoesNotExist:
            return JsonResponse({"message":"INVALID_ERROR"}, status=400)

class DealsView(View):
    @public_login
    def get(self, request):
        try:
            signed_user = request.user
            deal_closed = request.GET.get('closed', False)
            category    = request.GET.get('category', False)
            PAGE_SIZE   = 12
            q           = Q()
            offset      = int(request.GET.get('offset', 0))
            limit       = int(request.GET.get('limit', PAGE_SIZE)) + offset

            categories = {
                'mortgage'  : Deal.Category.MORTGAGE.value,
                'individual': Deal.Category.CREDIT.value
            }

            if category not in categories:
                return JsonResponse({"message":"INVALID_INPUT"}, status=400)

            q.add(Q(category=categories[category]), q.AND)
            
            if deal_closed == 'true' and categories[category] == Deal.Category.MORTGAGE.value:
                q.add(Q(end_date__lt=timezone.localdate()) | Q(net_reservation=F('net_amount')), q.AND)

            else:
                limit  = None
                q.add(Q(end_date__gte=timezone.localdate()) & Q(start_date__lte=timezone.localdate()), q.AND)

            deals = Deal.objects.annotate(net_reservation=Sum('userdeal__amount')).filter(q).prefetch_related(
                Prefetch('userdeal_set', queryset=UserDeal.objects.filter(user=signed_user), to_attr='userdeals'),
                Prefetch(
                    'mortgage_set', 
                    queryset=Mortgage.objects.prefetch_related(
                        Prefetch(
                            'mortgageimage_set', 
                            queryset=MortgageImage.objects.all(), 
                            to_attr='image')
                            ), to_attr='mortgages')
                    )

            results = [
                {
                    'index'           : deal.id,
                    'title'           : deal.name,
                    'grade'           : Deal.Grade(deal.grade).label,
                    'period'          : deal.repayment_period,
                    'earningRate'     : deal.earning_rate,
                    'amount'          : deal.net_amount,
                    'titleImage'      : deal.mortgages[0].image[0].image_url\
                                        if categories[category] == Deal.Category.MORTGAGE.value else None,
                    'startDate'       : deal.start_date,
                    'progress'        : math.trunc(((deal.net_reservation or 0) / deal.net_amount) * 100),
                    'investmentAmount': deal.net_reservation or 0,
                    'invested'        : True if deal.userdeals else False
                } for deal in deals[offset:limit]
            ]

            if deal_closed != 'true' and categories[category] == Deal.Category.MORTGAGE.value:
                scheduled_results = [
                    {
                        'index'      : deal.id,
                        'title'      : deal.name,
                        'period'     : deal.repayment_period,
                        'earningRate': deal.earning_rate,
                        'amount'     : deal.net_amount,
                        'titleImage' : deal.mortgages[0].image[0].image_url,
                        'startDate'  : deal.start_date
                    } for deal in Deal.objects.filter(status=Deal.Status.SCHEDULED.value, category=Deal.Category.MORTGAGE.value).prefetch_related(
                Prefetch(
                    'mortgage_set', 
                    queryset=Mortgage.objects.prefetch_related(
                        Prefetch(
                            'mortgageimage_set', 
                            queryset=MortgageImage.objects.all(), 
                            to_attr='image')
                            ), to_attr='mortgages'))
                ]

                return JsonResponse({"recruitingResults": results, "scheduledResults": scheduled_results}, status=200)
            
            return JsonResponse({"results":results, "count":len(deals)}, status=200)

        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"}, status=400)

class LoanAmountView(View):
    def get(self, request):
        result = {
            "loanAcc": UserDeal.objects.filter(deal__end_date__lt=timezone.localdate()).aggregate(Sum('amount'))['amount__sum'],
            "avgPerPerson": int(UserDeal.objects.aggregate(Sum('amount'))['amount__sum'] / User.objects.count()),
            "investAcc": UserDeal.objects.count()
        }

        return JsonResponse({"result": result}, status=200)

class DealPaybackView(View):
    @public_login
    def get(self, request, deal_id):
        user    = request.user
        deposit = user.deposit_amount if user else None

        options = {}

        deal = Deal.objects.get(id=deal_id)

        payback_schedules = PaybackSchedule.objects.filter(deal_id = deal_id)

        for payback_schedule in payback_schedules:
            if not options.get(payback_schedule.option):
                options[payback_schedule.option] = {
                    'realityPrice': payback_schedule.option,
                    'tax'         : 0,
                    'interest'    : 0,
                    'commission'  : 0
                }

            interest = payback_schedule.interest
            tax = payback_schedule.tax
            commission = payback_schedule.commission

            options[payback_schedule.option]['realityPrice'] += (interest - tax - commission)
            options[payback_schedule.option]['tax']          += tax
            options[payback_schedule.option]['interest']     += interest
            options[payback_schedule.option]['commission']   += commission

        results = {
            'deposit'     : deposit,
            'invested'    : UserDeal.objects.filter(user=user, deal_id=deal_id).exists(),
            'status'      : Deal.Status(deal.status).name,
            'investCount' : UserDeal.objects.filter(deal_id=deal_id).count(),
            'options'     : options
        }

        return JsonResponse({"results": results}, status=200)
